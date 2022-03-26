from django.http import JsonResponse
from api.db_connection import cur, conn
from api.auth import validateToken, getUserIdByToken, loggedUser, is_user_teacher
import json


def getUserMarks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=400)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=400)

    if is_user_teacher(request):
        return JsonResponse({'message': 'You are not a student'}, status=400)

    user_id = getUserIdByToken(request)

    query = "select u.id as user_id, u.name as name, u.surname as surname, m.mark as mark, t.name as task_name from marks as m join users as u on u.id = m.user_id join tasks as t on t.id = m.task_id where u.id = " + str(
        user_id)

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
            'mark': i[3],
            'task_name': i[4]
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
