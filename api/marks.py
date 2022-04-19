from django.http import JsonResponse
from api.db_connection import cur, conn
from api.auth import validateToken, getUserIdByToken, loggedUser, is_user_teacher, check_request
import json

def get_class_marks(request):
    error = check_request(request,
                          request_method='GET',
                          must_be_logged_in=True)
    if error:
        return error

    user_id = getUserIdByToken(request)
    query = "select class from users where id = " + str(user_id)
    cur.execute(query)
    class_id = cur.fetchall()

    if not class_id:
        return JsonResponse({'message': 'No users in this class'}, status=400)

    temp = {
        "marks": []
    }

    query = """
    select u.name as name, u.surname as surname, m.mark as mark,  m.id as mark_id,  t.name as task_name, t.subject as task_subject
    from marks as m 
    join users as u on u.id = m.user_id 
    join tasks as t on t.id = m.task_id 
    where u.class =  """ + str(class_id[0][0])
    cur.execute(query)
    result = cur.fetchall()

    for entry in result:
        temp["marks"].append({
            "name": entry[0],
            "surname": entry[1],
            "mark": entry[2],
            "mark_id": entry[3],
            "task_name": entry[4],
            "task_subject": entry[5]
        })

    return JsonResponse(temp, status=200)

def getUserMarks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=400)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=400)

    # if user is teacher, get him marks of his students
    if is_user_teacher(request):
        return get_class_marks(request)

    user_id = getUserIdByToken(request)

    query = """
    select u.id as user_id, u.name as name, u.surname as surname, m.mark as mark, t.name as task_name, m.id as mark_id, t.subject as task_subject
    from marks as m 
    join users as u on u.id = m.user_id 
    join tasks as t on t.id = m.task_id 
    where u.id =  """ + str(user_id)

    cur.execute(query)
    result = cur.fetchall()

    object = {
        'user_id': result[0][0],
        'name': result[0][1],
        'surname': result[0][2],
        'marks': []
    }
    for i in result:
        object['marks'].append({
            'mark_id': i[5],
            'mark': i[3],
            'task_name': i[4],
            'task_subject': i[6]
        })

    return JsonResponse(object, status=200)


# assign mark to student
def assignMark(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=400)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=400)

    if not is_user_teacher(request):
        return JsonResponse({'message': 'You are not a teacher'}, status=400)

    user_id = getUserIdByToken(request)  # teacher id - do we need it?

    data = request.body.decode('utf-8')
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Bad request'}, status=400)

    if 'mark' not in data or 'user_id' not in data or 'task_id' not in data:
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not isinstance(data['mark'], int):
        return JsonResponse({'message': 'Bad request'}, status=400)

    if data['mark'] < 1 or data['mark'] > 5:
        return JsonResponse({'message': 'Bad request'}, status=400)

    # do we need this?
    # if int(data['user_id']) != user_id:
    #    return JsonResponse({'message': 'You are not a teacher of this student'}, status=400)

    query = "select * from marks where user_id = " + str(data['user_id']) + " and task_id = " + str(data['task_id'])
    cur.execute(query)
    result = cur.fetchall()

    if len(result) > 0:
        return JsonResponse({'message': 'Mark already assigned'}, status=400)

    query = "insert into marks (mark, user_id, task_id) values (" + str(data['mark']) + ", " + str(data['user_id']) + ", " + str(data[
        'task_id']) + ")"
    cur.execute(query)
    conn.commit()

    return JsonResponse({'message': 'Mark assigned'}, status=200)


# delete mark from student
def deleteMark(request):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=400)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=400)

    if not is_user_teacher(request):
        return JsonResponse({'message': 'You are not a teacher'}, status=400)

    data = request.body.decode('utf-8')
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Bad request'}, status=400)

    if 'user_id' not in data or 'task_id' not in data:
        return JsonResponse({'message': 'Bad request'}, status=400)

    query = "select * from marks where user_id = " + str(data['user_id']) + " and task_id = " + str(data['task_id'])
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return JsonResponse({'message': 'Mark not found'}, status=400)

    query = "delete from marks where user_id = " + str(data['user_id']) + " and task_id = " + str(data['task_id'])
    cur.execute(query)
    conn.commit()

    return JsonResponse({'message': 'Mark deleted'}, status=200)


def update_mark(request):
    error = check_request(request,
                          request_method='PUT',
                          must_be_logged_in=True,
                          must_be_teacher=True,
                          required_fields=['mark_id', 'new_mark', 'new_task_id', 'new_user_id'])
    if error:
        return error

    data = json.loads(request.body.decode('utf-8'))
    cur.execute(f"select * from users where users.id = {data['new_user_id']}")
    result = cur.fetchall()
    if not result:
        return JsonResponse({'message': 'User id not found.'}, status=400)

    result.clear()
    cur.execute(f"select * from tasks where tasks.id = {data['new_task_id']}")
    result = cur.fetchall()
    if not result:
        return JsonResponse({'message': 'Task id not found.'}, status=400)

    result.clear()
    cur.execute(f"select * from marks where marks.id = {data['mark_id']}")
    result = cur.fetchall()
    if not result:
        return JsonResponse({'message': 'Mark id not found.'}, status=400)

    cur.execute(f"""
    update marks 
    set mark = {data['new_mark']}, user_id = {data['new_user_id']}, task_id = {data['new_task_id']} 
    where marks.id = {data['mark_id']}""")
    conn.commit()

    return JsonResponse({'message': 'Mark updated.'}, status=200)
