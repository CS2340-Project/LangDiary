from django.urls import path
from . import views

# This variable must be named 'urlpatterns' and must be a list
urlpatterns = [
    path('', views.home, name='home'),
    # Add other URL patterns here
]