from django.urls import path

from api.auth import login, logout, get_users_from_class, get_user_info
from api.tasks import print_tasks, create_new_task, delete_task, assign_task, update_task, get_all_tasks
from api.marks import getUserMarks, get_marks_by_user_id, assignMark, deleteMark, update_mark, delete_mark_new
from api.comments import get_comments_by_task_id, add_comment, delete_comment

urlpatterns = [
    path('user/login', login, name="login"),
    path('user/logout', logout, name="logout"),

    path('user/marks', getUserMarks, name="getUserMarks"),
    path('user/tasks', print_tasks, name="print_tasks"),
    path('user/class', get_users_from_class, name="get_users_from_class"),
    path('user/info', get_user_info, name="get_user_info"),     #nove api

    path('tasks/create', create_new_task, name='create_new_task'),
    path('tasks/delete', delete_task, name='delete_task'),
    path('tasks/assign', assign_task, name='assign_task'),
    path('tasks/update', update_task, name='update_task'),
    path('tasks/all', get_all_tasks, name='get_all_tasks'),

    path('comments/<int:task_id>', get_comments_by_task_id, name="get_comments_by_task_id"),
    path('comments/add', add_comment, name="add_comment"),
    path('comments/delete', delete_comment, name="delete_comment"),

    path('marks/get/<int:user_id>', get_marks_by_user_id, name="get_marks_by_user_id"),
    path('marks/assign', assignMark, name="assignMark"),
    path('marks/delete', delete_mark_new, name="delete_mark_new"),
    path('marks/update', update_mark, name='update_mark')
]
