from django.urls import path
from . import views

urlpatterns = [
    path('v1/test', views.test, name="test"),
]