import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .models import Place, Favorite
from .utils.langlocale import get_data

# Create your views here.
def index(request):

    userLocation = None
    if request.method == "POST":
        body = json.loads(request.body)
        if body['status']:
            userLocation = body['position']


    template_data = {'title': 'LangLocales'}
    data = get_data(userLocation)

    if request.user.is_authenticated:
        favorite_places = Favorite.objects.filter(user=request.user).values_list("place__placeId", flat=True)

    for datum in data:
        place = Place.objects.filter(placeId=datum['mapsUrl']).first()
        if not place:
            place = Place.objects.create(placeId=datum['mapsUrl'], placeName=datum['name'], placeImageUrl=datum['imageUrl'])


        if request.user.is_authenticated:
            datum['is_favorite'] = place.placeId in favorite_places
        else:
            datum['is_favorite'] = False
  #  print(data)
    return render(request, 'langlocale/index.html', {
        'place_data': data
    })


class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request):
        if request.method == 'POST':
            place_id = request.POST.get('place_id')
            place_name = request.POST.get('place_name')
            place_image_url = request.POST.get('place_image_url')

            place = Place.objects.filter(placeId=place_id).first()

            user = request.user
            favorite = Favorite.objects.filter(user=user, place=place).first()
            if favorite:
                favorite.delete()
            else:
                Favorite.objects.create(user=user, place=place)

        return redirect(reverse('langlocale:index'))