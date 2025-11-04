from django.urls import path
from . import views

app_name = 'speech'

urlpatterns = [
    path('deep-think/', views.deep_think, name='deep_think'),
    path('simple-response/', views.simple_response, name='simple_response'),
]