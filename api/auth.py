import json
import datetime
import jwt
from django.http import JsonResponse
from api.db_connection import cur


def check_request(request,
                  request_method: str = None,
                  must_be_logged_in: bool = False,
                  must_be_teacher: bool = False,
                  required_fields: list[str] = None,
                  ) -> JsonResponse or None:
    """
    Checks request for stuff specified in the parameters

    :parameter request: Request to be picked apart
    :param request_method: Type of request (GET, POST, PUT...), if not specified, accepts any
    :param must_be_logged_in: Whether the user must be logged in (True/False), default: False
    :param must_be_teacher: Whether the user must have teacher privileges (True/False), default: False
    :param required_fields: List of required fields in request.body json.
    """
    if request_method and request.method != request_method:
        return JsonResponse({'message': 'Bad request method'}, status=400)

    if must_be_logged_in and not validateToken(request):
        return JsonResponse({'message': 'Bad token'}, status=400)

    if must_be_logged_in and not loggedUser(request):
        return JsonResponse({'message': 'You are not logged in'}, status=401)

    if must_be_teacher and not is_user_teacher(request):
        return JsonResponse({'message': 'You are not authorized for this action'}, status=403)

    if required_fields:

        if not request.body and not request.POST:
            return JsonResponse({'message': 'No data'}, status=400)

        # if there is something in .POST, we ignore .body and decoding :shrug:
        if not request.POST:
            data = request.body.decode('utf-8')
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Bad request'}, status=400)
        else:
            data = request.POST

        # if anything is left in the checklist then something required is missing
        checklist = required_fields.copy()
        for item in required_fields:
            if item in data:
                checklist.remove(item)

        if checklist:
            return JsonResponse({'message': 'Missing required fields', 'Items': checklist}, status=400)

    return None


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
    return JsonResponse({'login_token': token}, status=200)


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


# get all users from one class
def get_users_from_class(request):
    error = check_request(request,
                          request_method='GET',
                          must_be_logged_in=True)
    if error:
        return error

    user_id = getUserIdByToken(request)
    query = "select class from users where id = " + str(user_id)
    cur.execute(query)
    result = cur.fetchall()

    query = "select * from users where class = " + str(result[0][0])
    cur.execute(query)
    result = cur.fetchall()

    if not result:
        return JsonResponse({'message': 'No users in this class'}, status=400)

    object = {
        'users': []
    }
    for i in result:
        object['users'].append({
            'id': i[0],
            'name': i[1],
            'surname': i[2],
            'email': i[3],
            'class': i[6],
            'teacher': i[5]
        })

    return JsonResponse(object, status=200)


# get user info
def get_user_info(request):
    error = check_request(request,
                          request_method='GET',
                          must_be_logged_in=True)
    if error:
        return error

    user_id = getUserIdByToken(request)
    query = "select * from users where id = " + str(user_id)
    cur.execute(query)
    result = cur.fetchall()

    if not result:
        return JsonResponse({'message': 'No user with this id'}, status=400)

    object = {
        'id': result[0][0],
        'name': result[0][1],
        'surname': result[0][2],
        'email': result[0][3],
        'teacher': result[0][5],
        'class': result[0][6]
    }

    return JsonResponse(object, status=200)

