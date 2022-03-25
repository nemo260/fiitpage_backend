from django.urls import path

from api.auth import login,logout
from api.tasks import print_tasks
from api.marks import getUserMarks

urlpatterns = [
    path('user/login', login, name="login"),
    path('user/logout', logout, name="logout"),

    path('user/marks', getUserMarks, name="getUserMarks"),
    path('user/tasks', print_tasks, name="print_tasks"),
]