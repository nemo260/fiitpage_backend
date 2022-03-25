from django.http import JsonResponse
from django.http import HttpResponse
from api.auth import validateToken,loggedUser
from api.db_connection import cur

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