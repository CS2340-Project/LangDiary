import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
import os 
from .utils.langlocale import get_data
from .utils.langlocale import get_coordinates_for_place_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Place, Favorite, Comment

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
        datum['favorite_count'] = Favorite.objects.filter(place=place).count()

    print(datum)
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
    comments = Comment.objects.filter(placeId=place).order_by('-id')

    if request.method == 'POST' and request.user.is_authenticated:
        comment_id = request.POST.get('comment_id')

        # Delete comment
        if 'delete_comment' in request.POST:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            comment.delete()
            messages.success(request, "Comment deleted successfully.")
            return redirect('langlocale:details', placeId=placeId)

        # Edit comment
        elif 'edit_comment' in request.POST:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            comment.text = request.POST.get('comment_text')
            comment.save()
            messages.success(request, "Comment updated successfully.")
            return redirect('langlocale:details', placeId=placeId)

        # Add new comment
        else:
            comment_text = request.POST.get('comment')
            if comment_text:
                Comment.objects.create(
                    text=comment_text,
                    user=request.user,
                    placeId=place
                )
                messages.success(request, "Comment added successfully.")
            return redirect('langlocale:details', placeId=placeId)

    return render(request, "langlocale/details.html", {
        'place': place,
        'comments': comments,
        "key": os.getenv("PLACES_API_KEY")
    })

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