from django.http import JsonResponse
from api.db_connection import cur
from api.auth import validateToken, getUserIdByToken, loggedUser


def getUserMarks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    user_id = getUserIdByToken(request)


    query = "select u.id as user_id, u.name as name, u.surname as surname, m.mark as mark, t.name as task_name from marks as m join users as u on u.id = m.user_id join tasks as t on t.id = m.task_id where u.id = " + str(user_id)

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