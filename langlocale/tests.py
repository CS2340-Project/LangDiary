from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import Place, Favorite
from unittest.mock import patch
from .utils.langlocale import get_data

class PlaceCreationTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client = Client()
        self.client.login(username='testuser', password='securepassword123')

    def test_index_creates_new_place(self):

        self.assertEqual(Place.objects.count(), 0)

        response = self.client.get(reverse('langlocale:index'))
        response_data = response.context['place_data']
        actual_data = get_data(None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data), max(12, len(response_data)))

        for entry in actual_data:
            place = Place.objects.filter(placeId=entry['mapsUrl']).first()
            self.assertTrue(place)
            self.assertEqual(place.placeName, entry['name'])


class FavoriteTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        self.user = User.objects.create_user(**self.user_data)

        # Create a test place
        self.place = Place.objects.create(
            placeId='test_place_123',
            placeName='Test Place',
            placeImageUrl='https://example.com/image.jpg'
        )

        # Set up client
        self.client = Client()
        self.client.login(username='testuser', password='securepassword123')

    def test_add_to_favorites(self):
        self.assertEqual(Favorite.objects.count(), 0)

        response = self.client.post(reverse('langlocale:add_to_favorites'), {
            'place_id': self.place.placeId,
            'place_name': self.place.placeName,
            'place_image_url': self.place.placeImageUrl
        })

        self.assertRedirects(response, reverse('langlocale:index'))

        self.assertEqual(Favorite.objects.count(), 1)
        favorite = Favorite.objects.first()
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.place, self.place)

    def test_toggle_favorite_removes_existing(self):
        Favorite.objects.create(user=self.user, place=self.place)
        self.assertEqual(Favorite.objects.count(), 1)

        response = self.client.post(reverse('langlocale:add_to_favorites'), {
            'place_id': self.place.placeId,
            'place_name': self.place.placeName,
            'place_image_url': self.place.placeImageUrl
        })

        self.assertEqual(Favorite.objects.count(), 0)

    def test_login_required_for_favorites(self):
        # Log out
        self.client.logout()

        response = self.client.post(reverse('langlocale:add_to_favorites'), {
            'place_id': self.place.placeId,
            'place_name': self.place.placeName,
            'place_image_url': self.place.placeImageUrl
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login/?next=/langlocale/add_to_favorites")
        self.assertEqual(Favorite.objects.count(), 0)