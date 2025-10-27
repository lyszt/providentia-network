from django.urls import path
from . import views

app_name = 'speech'

urlpatterns = [
    path('simple_response', views.simple_response, name='simple_response'),
]