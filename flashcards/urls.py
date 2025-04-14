from django.urls import path
from . import views
from . import api_views
urlpatterns = [
    path('', views.index, name='flashcards.index'),
    path('create/', views.create_flashcard, name='flashcards.create_flashcard'),
    path('update/', views.update_flashcard, name='flashcards.update_flashcard'),
    path('delete/', views.delete_flashcard, name='flashcards.delete_flashcard'),
    path('mark-reviewed/', views.mark_reviewed, name='flashcards.mark_reviewed'),
    path('generate/', views.generate_flashcards, name='flashcards.generate'),
    path('api/card/<int:card_id>/', api_views.get_card, name='flashcards.api.get_card'),
    path('api/indicators/', api_views.get_indicators, name='flashcards.api.get_indicators'),
    path('api/mark-reviewed/', api_views.mark_reviewed_api, name='flashcards.api.mark_reviewed'),
    path('api/delete/', api_views.delete_flashcard_api, name='flashcards.api.delete_flashcard'),

]