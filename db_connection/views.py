from django.shortcuts import render
import psycopg2, os
from django.http import JsonResponse
from django.http import HttpResponse
import json
# Create your views here.


def test(request):
    conn = psycopg2.connect(database=os.getenv('DATABASE_NAME'), user=os.getenv('DATABASE_USER'),
                            password=os.getenv('DATABASE_PASSWORD'), host=os.getenv('DATABASE_HOST'),
                            port=os.getenv('DATABASE_PORT'))

    query = "SELECT * from users"

    cur = conn.cursor()
    cur.execute(query)

    return HttpResponse(cur)