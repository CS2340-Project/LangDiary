from django.urls import path
from . import views

app_name = 'calendar_integration'

urlpatterns = [
    path('oauth2login/', views.oauth2login, name='oauth2login'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('add_event/', views.add_event, name='add_event'),
]