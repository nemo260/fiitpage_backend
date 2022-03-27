from django.http import JsonResponse
from django.http import HttpResponse
from api.auth import validateToken, loggedUser, getUserIdByToken
from api.db_connection import cur, conn
import json, datetime
import jwt


def get_comments_by_task_id(request, task_id: int):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    query = """
    select c.task_id,c.comment as comment, u.name as author_name, u.surname as author_surname
    from comments as c
    join users as u
    on c.user_id = u.id
    where c.task_id = 
    """ + str(task_id) + ';'

    cur.execute(query)
    result = cur.fetchall()

    object = {
        'task_id': task_id,
        'number_of_comments': len(result),
        'comments': []
    }

    for i in result:
        object['comments'].append({
            'text': i[1],
            'author_name': i[2],
            'author_surname': i[3]
        })

    return JsonResponse(object, status=200)


def add_comment(request, task_id: int):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if not request.body:
        return JsonResponse({'message': 'No data'}, status=400)

    user_id = getUserIdByToken(request)

    data = request.body.decode('utf-8')
    data = json.loads(data)

    if 'comment' not in data:
        return JsonResponse({'message': 'No comment'}, status=400)

    query = "insert into comments (comment, user_id, task_id) values ('" + data['comment'] + "'," + str(user_id) + ",'" + str(task_id) + "');"

    cur.execute(query)
    conn.commit()
    return JsonResponse({'message': 'Added comment'}, status=201)


def delete_comment(request):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    if not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if not request.body:
        return JsonResponse({'message': 'No data'}, status=400)

    data = request.body.decode('utf-8')
    data = json.loads(data)
    user_id = getUserIdByToken(request)

    if 'comment_id' not in data:
        return JsonResponse({'message': 'No comment id'}, status=400)

    query = "select * from comments where id = " + str(data['comment_id']) + " and user_id = " + str(user_id) + ";"
    cur.execute(query)
    result = cur.fetchall()

    if not result:
        return JsonResponse({'message': 'No match comment_id with user_id'}, status=400)

    query = "delete from comments where id = " + str(data['comment_id']) + ";"
    cur.execute(query)
    conn.commit()
    return JsonResponse({'message': 'Deleted comment'}, status=200)

