from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.landing'),
    path('about', views.about, name='home.about'),
]