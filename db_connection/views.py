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


def test(request):
    query = "SELECT * from users"

    cur.execute(query)

    return HttpResponse(cur)


def print_tasks(request, user_id):

    if request.method != 'GET':
        return JsonResponse({'message': 'Bad request'}, status=400)

    if not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=401)

    query = "select u.id as user_id, u.name as name, u.surname as surname, t.name as task_name, t.subject as subject from users as u, tasks as t, user_tasks as ut where u.id = ut.user_id and t.id = ut.task_id and u.id = " + str(user_id)

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


def login(request):
    if request.method == 'POST':
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
        return JsonResponse({'token': token}, status=200)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)