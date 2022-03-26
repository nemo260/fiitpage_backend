import json, datetime
import jwt

from django.http import JsonResponse
from api.db_connection import cur


# check if user is logged in
def loggedUser(request):
    token = request.headers['Authorization'].split(' ')[1]
    token = jwt.decode(token, 'secret', algorithms='HS256')

    if token['id'] == 82548254:
        return False
    else:
        return True


# check if user is teacher
def is_user_teacher(request):
    token = request.headers['Authorization'].split(' ')[1]
    token = jwt.decode(token, 'secret', algorithms='HS256')

    query = "select * from users where id = " + str(token['id'])
    cur.execute(query)
    result = cur.fetchall()

    if result[0][5]:
        return True
    else:
        return False


# check if token is valid
def validateToken(request):
    try:
        token = request.headers['Authorization'].split(' ')[1]
        token = jwt.decode(token, 'secret', algorithms='HS256')
    except:
        return False

    return True


# get current user id
def getUserIdByToken(request):
    token = request.headers['Authorization'].split(' ')[1]
    token = jwt.decode(token, 'secret', algorithms='HS256')

    return token['id']


# login user and return token
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


# useless function for this time :)
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