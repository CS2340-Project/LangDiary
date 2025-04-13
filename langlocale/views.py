import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
import os 
from .models import Place, Favorite
from .utils.langlocale import get_data
from .utils.langlocale import get_coordinates_for_place_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
            place = Place.objects.create(placeId=datum['mapsUrl'], placeName=datum['name'],
                                         placeImageUrl=datum['imageUrl'],
                                         placeLoc=get_coordinates_for_place_id(datum['id']))
        if request.user.is_authenticated:
            datum['is_favorite'] = place.placeId in favorite_places
        else:
            datum['is_favorite'] = False

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(data, 12)  # 12 items per page

    try:
        places = paginator.page(page)
    except PageNotAnInteger:
        places = paginator.page(1)
    except EmptyPage:
        places = paginator.page(paginator.num_pages)

    return render(request, 'langlocale/index.html', {
        'place_data': places,
        'template_data': template_data,
        'paginator': paginator,
    })


def details(request, placeId):
    full_id = f"https://www.google.com/maps/place/?q=place_id:{placeId}"
    place = get_object_or_404(Place, placeId=full_id)

    print("[DEBUG] Place retrieved:")
    print("Name:", place.placeName)
    print("Image:", place.placeImageUrl)
    print("Loc:", place.placeLoc)

    return render(request, "langlocale/details.html", {'place': place, "key": os.getenv("PLACES_API_KEY") })


class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request):
        if request.method == 'POST':
            place_id = request.POST.get('place_id')
            place_name = request.POST.get('place_name')
            place_image_url = request.POST.get('place_image_url')
            place_loc = request.POST.get('place_loc')
            place = Place.objects.filter(placeId=place_id).first()

            user = request.user
            favorite = Favorite.objects.filter(user=user, place=place).first()
            if favorite:
                favorite.delete()
            else:
                Favorite.objects.create(user=user, place=place)

        return redirect(reverse('langlocale:index'))