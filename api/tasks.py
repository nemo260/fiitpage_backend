import json
from django.http import JsonResponse
from api.auth import validateToken, loggedUser, getUserIdByToken, is_user_teacher
from api.db_connection import cur, conn
import json


def print_tasks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    user_id = getUserIdByToken(request)

    query = """
    select u.id as user_id, u.name as name, u.surname as surname, t.name as task_name, t.subject as subject, t.data as data
    from users as u, tasks as t, user_tasks as ut 
    where u.id = ut.user_id and t.id = ut.task_id and u.id = 
    """ + str(user_id)

    cur.execute(query)
    result = cur.fetchall()

    object = {
        'user_id': result[0][0],
        'name': result[0][1],
        'surname': result[0][2],
        'tasks': []
    }
    for i in result:
        object['tasks'].append({
            'task_name': i[3],
            'subject': i[4],
            'data': None if i[5] is None else bytes(i[5]).hex()
        })

    return JsonResponse(object, status=200)


def create_new_task(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not is_user_teacher(request):
        return JsonResponse({'message': 'You are not authorized for this action'})

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if not request.body:
        return JsonResponse({'message': 'No data'}, status=400)

    data = json.loads(request.body.decode())
    error_list = []

    if 'name' not in data:
        error_list.append('missing name')

    if 'subject' not in data:
        error_list.append('missing subject')

    # :shrug:
    # if 'data' not in data:
    #     error_list.append('missing data')

    if len(error_list):
        return JsonResponse({'errors': error_list})

    # V mojom fejkovom pythonovskom "frontende" sa data premenia na string metodou .hex(), takze tuna sa dekoduju
    data['data'] = bytes.fromhex(data['data'])

    cur.execute('''INSERT INTO tasks(name, subject, data) VALUES (%s, %s, %s)''', (data['name'], data['subject'], data['data']))
    conn.commit()

    return JsonResponse({"message": "successfully added task"})


def delete_task(request):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if not is_user_teacher(request):
        return JsonResponse({'message': 'You are not authorized for this action'}, status=401)

    if not request.body:
        return JsonResponse({'message': 'No data'}, status=400)

    data = json.loads(request.body.decode())

    if 'task_id' not in data:
        return JsonResponse({'message': 'No task id'}, status=400)

    query = """select * from tasks where id = """ + str(data['task_id'])
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return JsonResponse({'message': 'No task with this id'}, status=400)

    cur.execute('''delete from user_tasks where task_id = %s''', (data['task_id'],))
    conn.commit()

    cur.execute('''delete from comments where task_id = %s''', (data['task_id'],))
    conn.commit()

    cur.execute('''delete from marks where task_id = %s''', (data['task_id'],))
    conn.commit()

    cur.execute('''DELETE FROM tasks WHERE id = %s''', (data['task_id'],))
    conn.commit()

    return JsonResponse({"message": "successfully deleted task"}, status=200)


# assign task to student
def assign_task(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if not is_user_teacher(request):
        return JsonResponse({'message': 'You are not authorized for this action'}, status=401)

    if not request.body:
        return JsonResponse({'message': 'No data'}, status=400)

    data = json.loads(request.body.decode())

    if 'task_id' not in data:
        return JsonResponse({'message': 'No task id'}, status=400)

    if 'student_id' not in data:
        return JsonResponse({'message': 'No student id'}, status=400)

    query = """select * from tasks where id = """ + str(data['task_id'])
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return JsonResponse({'message': 'No task with this id'}, status=400)

    for i in data['student_id']:
        cur.execute('''select * from users where id = %s''', str(i))
        result = cur.fetchall()
        if len(result) == 0:
            return JsonResponse({'message': 'No student with this id'}, status=400)

    for i in data['student_id']:
        cur.execute('''select * from users where role = true and id = %s''', str(i))
        result = cur.fetchall()
        if len(result):
            return JsonResponse({'message': 'You can not assign task to teacher'}, status=400)

    for i in data['student_id']:
        cur.execute('''select * from user_tasks where task_id = %s and user_id = %s''', (data['task_id'], str(i)))
        result = cur.fetchall()
        if len(result) != 0:
            return JsonResponse({'message': 'Student already assigned to this task'}, status=400)

    for i in data['student_id']:
        cur.execute('''INSERT INTO user_tasks(user_id, task_id) VALUES (%s, %s)''', (str(i), data['task_id']))
        conn.commit()

    return JsonResponse({"message": "successfully assigned task"}, status=200)

