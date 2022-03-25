from django.shortcuts import render
import psycopg2, os
from django.http import JsonResponse
from django.http import HttpResponse
import json, datetime
import jwt
import environ
# Create your views here.

env = environ.Env()
environ.Env.read_env()
conn = psycopg2.connect(database=env('db_name'), user=env('db_user'),
                        password=env('db_password'), host=env('db_host'),
                        port=env('db_port'))
cur = conn.cursor()


def loggedUser(request):
    token = request.headers['Authorization'].split(' ')[1]
    token = jwt.decode(token, 'secret', algorithms='HS256')

    if token['id'] == 82548254:
        return False
    else:
        return True


def validateToken(request):
    try:
        token = request.headers['Authorization'].split(' ')[1]
        token = jwt.decode(token, 'secret', algorithms='HS256')
    except:
        return False

    return True


def getUserIdByToken(request):
    token = request.headers['Authorization'].split(' ')[1]
    token = jwt.decode(token, 'secret', algorithms='HS256')

    return token['id']


def login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    body = request.body.decode('utf-8')
    dict = json.loads(body)
    query = "select * from users where email = '" + dict['email'] + "' and password = '" + dict['password'] + "'"

    cur.execute(query)
    result = cur.fetchall()

    if not result:
        return JsonResponse({'message': 'Wrong password or email'}, status=400)

    header = {
        'id': result[0][0],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(header, 'secret', algorithm='HS256').decode('utf-8')
    return JsonResponse({'login token': token}, status=200)


def logout(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    header = {
        'id': 82548254,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(header, 'secret', algorithm='HS256').decode('utf-8')
    return JsonResponse({'logout token': token}, status=200)


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


def getUserMarks(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

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
