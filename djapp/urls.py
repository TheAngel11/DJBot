from django.urls import path
from . import views

urlpatterns = [
    path('getmessage/', views.get_message, name='getmessage'),
]