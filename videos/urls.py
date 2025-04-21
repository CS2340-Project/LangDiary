from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_videos, name='generate'),
    path('mark-watched/', views.mark_watched, name='mark_watched'),
    path('remove-video/', views.remove_video, name='remove_video'),
    path('daily/', views.daily_video, name='daily'),
    path('test-api/', views.test_youtube_api, name='test_api'),
]