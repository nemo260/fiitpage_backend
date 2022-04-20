import json
from django.http import JsonResponse
from api.auth import getUserIdByToken, check_request, is_user_teacher
from api.db_connection import cur, conn

def get_all_tasks(request):
    error = check_request(request,
                          request_method='GET',
                          must_be_logged_in=True,
                          must_be_teacher=True)
    if error:
        return error

    query = """
    select u.id as user_id, u.name as name, u.surname as surname, t.id as task_id, t.name as task_name, t.subject as subject, t.data as data
    from users as u, tasks as t, user_tasks as ut 
    where u.id = ut.user_id and t.id = ut.task_id"""
    cur.execute(query)
    result = cur.fetchall()

    if len(result) == 0 or len(result[0]) == 0:
        return JsonResponse({'message': 'No tasks'}, status=200)

    object = {
        'user_id': result[0][0],
        'name': result[0][1],
        'surname': result[0][2],
        'tasks': []
    }
    for i in result:
        object['tasks'].append({
            'task_id': i[3],
            'task_name': i[4],
            'subject': i[5],
            'data': None if i[6] is None else bytes(i[6]).hex()
        })

    return JsonResponse(object, status=200)

def print_tasks(request):
    error = check_request(request,
                          request_method='GET',
                          must_be_logged_in=True)
    if error:
        return error

    user_id = getUserIdByToken(request)

    if is_user_teacher(request):
        return get_all_tasks(request)
        # return JsonResponse({'message': 'You are not a student'}, status=400)

    query = """
    select u.id as user_id, u.name as name, u.surname as surname, t.id as task_id, t.name as task_name, t.subject as subject, t.data as data
    from users as u, tasks as t, user_tasks as ut 
    where u.id = ut.user_id and t.id = ut.task_id and u.id = 
    """ + str(user_id)

    cur.execute(query)
    result = cur.fetchall()

    if len(result) == 0:
        return JsonResponse({'message': 'No tasks'}, status=200)

    object = {
        'user_id': result[0][0],
        'name': result[0][1],
        'surname': result[0][2],
        'tasks': []
    }
    for i in result:
        object['tasks'].append({
            'task_id': i[3],
            'task_name': i[4],
            'subject': i[5],
            'data': None if i[6] is None else bytes(i[6]).hex()
        })

    return JsonResponse(object, status=200)


#def create_new_task(request):
#    error = check_request(request,
#                          request_method='POST',
#                          must_be_logged_in=True,
#                          must_be_teacher=True,
#                          required_fields=['name', 'subject'])
#    if error:
#        return error
#
#    # data = json.loads(request.body.decode())
#    data = request.POST.copy()
#
#    if request.FILES.get('data'):
#        data['data'] = request.FILES.get('data').file.read()
#    else:
#        return JsonResponse({'message': 'No file'}, status=400)
#
#    # print(data['data'])
#
#    cur.execute('''
#    INSERT INTO tasks(name, subject, data)
#    VALUES (%s, %s, %s)''', (data['name'], data['subject'], data['data'].encode() if data['data'] is not None else 'null'))
#    conn.commit()
#
#    return JsonResponse({"message": "successfully added task"})
def create_new_task(request):
    error = check_request(request,
                          request_method='POST',
                          must_be_logged_in=True,
                          must_be_teacher=True,
                          required_fields=['name', 'subject'])
    if error:
        return error

    data = request.body.decode('utf-8')
    data = json.loads(data)

    cur.execute('''
    INSERT INTO tasks(name, subject, data) 
    VALUES (%s, %s, %s)''', (data['name'], data['subject'], data['data'] if data['data'] is not None else 'null'))
    conn.commit()

    return JsonResponse({"message": "successfully added task"})


def delete_task(request):
    error = check_request(request,
                          request_method='DELETE',
                          must_be_logged_in=True,
                          must_be_teacher=True,
                          required_fields=['task_id'])
    if error:
        return error

    data = json.loads(request.body.decode())

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
    error = check_request(request, request_method='POST',
                          must_be_logged_in=True,
                          must_be_teacher=True,
                          required_fields=['task_id', 'student_id'])
    if error:
        return error

    data = json.loads(request.body.decode())

    query = """select * from tasks where id = """ + str(data['task_id'])
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return JsonResponse({'message': 'No task with this id'}, status=400)

    # for i in data['student_id']:
    cur.execute('''select * from users where id = %s''', str(data['student_id']))
    result = cur.fetchall()
    if len(result) == 0:
        return JsonResponse({'message': 'No student with this id'}, status=400)

    cur.execute('''select * from users where role = true and id = %s''', str(data['student_id']))
    result = cur.fetchall()
    if len(result):
        return JsonResponse({'message': 'You can not assign task to teacher'}, status=400)

    cur.execute('''select * from user_tasks where task_id = %s and user_id = %s''', (data['task_id'], str(data['student_id'])))
    result = cur.fetchall()
    if len(result) != 0:
        return JsonResponse({'message': 'Student already assigned to this task'}, status=200)


    cur.execute('''INSERT INTO user_tasks(user_id, task_id) VALUES (%s, %s)''', (str(data['student_id']), data['task_id']))
    conn.commit()

    return JsonResponse({"message": "successfully assigned task"}, status=200)


def update_task(request):
    error = check_request(request,
                          request_method='PUT',
                          must_be_logged_in=True,
                          must_be_teacher=True,
                          required_fields=['task_id', 'name', 'subject'])
    if error:
        return error

    data = json.loads(request.body.decode())

    cur.execute(f'''select * from tasks as t where t.id = {data['task_id']}''')
    result = cur.fetchall()
    if not len(result):
        return JsonResponse({'message': 'No task with this id'}, status=400)

    cur.execute(f'''
    update tasks 
    set name=%s, subject=%s, data=%s
    where tasks.id = {data['task_id']};''',
                (data['name'], data['subject'], data['data'] if 'data' in data.keys() else 'null'))
    conn.commit()

    return JsonResponse({'message': 'Successfully updated task'}, status=200)
