from django.urls import path

from api.auth import login,logout, get_users_from_class
from api.tasks import print_tasks, create_new_task, delete_task, assign_task, update_task
from api.marks import getUserMarks, assignMark, deleteMark, update_mark
from api.comments import get_comments_by_task_id, add_comment, delete_comment

urlpatterns = [
    path('user/login', login, name="login"),
    path('user/logout', logout, name="logout"),

    path('user/marks', getUserMarks, name="getUserMarks"),
    path('user/tasks', print_tasks, name="print_tasks"),
    path('user/class', get_users_from_class, name="get_users_from_class"),

    path('tasks/create', create_new_task, name='create_new_task'),
    path('tasks/delete', delete_task, name='delete_task'),
    path('tasks/assign', assign_task, name='assign_task'),
    path('tasks/update', update_task, name='update_task'),

    path('comments/<int:task_id>', get_comments_by_task_id, name="get_comments_by_task_id"),
    path('comments/add/<int:task_id>', add_comment, name="add_comment"),
    path('comments/delete', delete_comment, name="delete_comment"),

    path('marks/assign', assignMark, name="assignMark"),
    path('marks/delete', deleteMark, name="deleteMark"),
    path('marks/update', update_mark, name='update_mark')
]
