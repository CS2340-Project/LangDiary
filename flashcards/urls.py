from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='flashcards.index'),
    path('create/', views.create_flashcard, name='flashcards.create_flashcard'),
    path('update/', views.update_flashcard, name='flashcards.update_flashcard'),
    path('delete/', views.delete_flashcard, name='flashcards.delete_flashcard'),
    path('mark-reviewed/', views.mark_reviewed, name='flashcards.mark_reviewed'),
]