from django.urls import path
from . import views
app_name = 'exercises' 
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_exercise, name='create'),
    path('create_page/', views.create_page, name="create_page")
]