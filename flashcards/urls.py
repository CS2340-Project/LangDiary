from django.urls import path
from . import views

urlpatterns = [
 path('', views.index, name='flashcards.index'),
 path('create_flashcard/', views.create_flashcard, name='flashcards.create_flashcard'),
 path('update_flashcard/', views.update_flashcard, name='flashcards.update_flashcard'),
 path('delete_flashcard/', views.delete_flashcard, name='flashcards.delete_flashcard'),
 path('mark_reviewed/', views.mark_reviewed, name='flashcards.mark_reviewed'),
]
