from django.http import JsonResponse
from api.auth import validateToken, loggedUser, getUserIdByToken
from api.db_connection import cur


def print_tasks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    user_id = getUserIdByToken(request)

    query = "select u.id as user_id, u.name as name, u.surname as surname, t.name as task_name, t.subject as subject from users as u, tasks as t, user_tasks as ut where u.id = ut.user_id and t.id = ut.task_id and u.id = " + str(
        user_id)

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
            'subject': i[4]
        })

    return JsonResponse(object, status=200)