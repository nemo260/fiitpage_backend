from django.urls import path
from . import views

urlpatterns = [
    path('v1/test', views.test, name="test"),
    path('user/tasks', views.print_tasks, name="print_tasks"),
    path('user/login', views.login, name="login"),
    path('user/marks', views.getUserMarks, name="getUserMarks")
]