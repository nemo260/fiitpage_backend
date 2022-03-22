from django.shortcuts import render
import psycopg2, os
from django.http import JsonResponse
from django.http import HttpResponse
import json
# Create your views here.

def connect_to_db():
    conn = psycopg2.connect(database=os.getenv('DATABASE_NAME'), user=os.getenv('DATABASE_USER'),
                            password=os.getenv('DATABASE_PASSWORD'), host=os.getenv('DATABASE_HOST'),
                            port=os.getenv('DATABASE_PORT'))

    return conn


def test(request):
    conn = connect_to_db()

    query = "SELECT * from users"

    cur = conn.cursor()
    cur.execute(query)

    return HttpResponse(cur)


def print_tasks(request, user_id):
    conn = connect_to_db()

    query = "select u.id as user_id, u.name as name, u.surname as surname, t.name as task_name, t.subject as subject from users as u, tasks as t, user_tasks as ut where u.id = ut.user_id and t.id = ut.task_id and u.id = " + str(user_id)

    cur = conn.cursor()
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

    return JsonResponse(object)
