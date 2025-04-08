from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='users.register'),
    path('profile/', views.profile, name='users.profile'),
    path('create-goal/', views.create_goal, name='users.create_goal'),
    path('goal/<int:goal_id>/edit/', views.edit_goal, name='users.edit_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_goal, name='users.delete_goal'),
    path('goal/<int:goal_id>/update-progress/', views.update_goal_progress, name='users.update_goal_progress'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='users.login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='users.logout'),
    path('delete_profile_picture/', views.delete_profile_picture, name='users.delete_profile_picture'),
    path('users/create-goal/', views.create_goal, name='users.create_goal')
]
