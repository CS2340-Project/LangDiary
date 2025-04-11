from django.urls import path
from . import views


app_name = 'langlocale'

urlpatterns = [
 path('', views.index, name='index'),
 path('add_to_favorites', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
 path('details', views.details, name='details')
]