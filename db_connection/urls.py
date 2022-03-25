from django.urls import path
from . import views

urlpatterns = [
    path('user/login', views.login, name="login"),
    path('user/logout', views.logout, name="logout"),

    path('user/marks', views.getUserMarks, name="getUserMarks"),
    path('user/tasks', views.print_tasks, name="print_tasks"),

]