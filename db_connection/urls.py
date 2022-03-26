from django.urls import path

from api.auth import login,logout
from api.tasks import print_tasks
from api.marks import getUserMarks, assignMark
from api.comments import get_comments_by_task_id, add_comment

urlpatterns = [
    path('user/login', login, name="login"),
    path('user/logout', logout, name="logout"),

    path('user/marks', getUserMarks, name="getUserMarks"),
    path('user/tasks', print_tasks, name="print_tasks"),

    path('comments/<int:task_id>', get_comments_by_task_id, name="get_comments_by_task_id"),
    path('comments/add/<int:task_id>', add_comment, name="add_comment"),

    path('marks/assign', assignMark, name="assignMark"),
]