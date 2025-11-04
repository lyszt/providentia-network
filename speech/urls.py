from django.urls import path
from . import views

app_name = 'speech'

urlpatterns = [
    path('deepthink/', views.deep_think, name='deep_think'),
    path('answer/', views.simple_response, name='simple_response'),
]