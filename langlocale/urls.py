from django.urls import path
from . import views


urlpatterns = [
 path('', views.index, name='langlocale.index'),
 path('add_to_favorites', views.AddToFavoritesView.as_view(), name='langlocale.add_to_favorites'),
]