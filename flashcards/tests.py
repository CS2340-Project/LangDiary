from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from flashcards.models import Flashcard

class FlashcardModelTests(TestCase):
    def test_discovery(self):
        """Simple test to verify test discovery is working"""
        self.assertTrue(True)

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.flashcard = Flashcard.objects.create(
            user=self.user,
            front_text='Test Front',
            back_text='Test Back',
            num_revisions=0
        )

    def test_flashcard_creation(self):
        self.assertEqual(self.flashcard.front_text, 'Test Front')
        self.assertEqual(self.flashcard.back_text, 'Test Back')
        self.assertEqual(self.flashcard.num_revisions, 0)
        self.assertEqual(self.flashcard.user, self.user)

    def test_flashcard_str_method(self):
        self.assertEqual(str(self.flashcard), 'Test Front Test Back 0')

    def test_flashcard_ordering(self):
        # Create another flashcard with more revisions
        flashcard2 = Flashcard.objects.create(
            user=self.user,
            front_text='Test Front 2',
            back_text='Test Back 2',
            num_revisions=1
        )

        # Cards should be ordered by num_revisions
        cards = list(Flashcard.objects.all())
        self.assertEqual(cards[0].front_text, 'Test Front')
        self.assertEqual(cards[1].front_text, 'Test Front 2')


class FlashcardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.flashcard1 = Flashcard.objects.create(
            user=self.user,
            front_text='Card 1 Front',
            back_text='Card 1 Back',
            num_revisions=0
        )
        self.flashcard2 = Flashcard.objects.create(
            user=self.user,
            front_text='Card 2 Front',
            back_text='Card 2 Back',
            num_revisions=1
        )

    def test_index_view_requires_login(self):
        response = self.client.get(reverse('flashcards.index'))
        self.assertNotEqual(response.status_code, 200)

        # Login and try again
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('flashcards.index'))
        self.assertEqual(response.status_code, 200)

    def test_index_view_with_cards(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('flashcards.index'))

        self.assertEqual(response.status_code, 200)
        # Check for card-box element with correct data-card-id
        self.assertContains(response, f'data-card-id="{self.flashcard1.id}"')
        self.assertEqual(response.context['current_card'], self.flashcard1)
        self.assertEqual(response.context['next_card_id'], self.flashcard2.id)
        self.assertIsNone(response.context['prev_card_id'])


    def test_index_view_with_specific_card(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(f"{reverse('flashcards.index')}?card_id={self.flashcard2.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_card'], self.flashcard2)
        self.assertEqual(response.context['prev_card_id'], self.flashcard1.id)
        self.assertIsNone(response.context['next_card_id'])

    def test_create_flashcard(self):
        self.client.login(username='testuser', password='password123')

        # Test POST request
        response = self.client.post(reverse('flashcards.create_flashcard'), {
            'front_text': 'New Front',
            'back_text': 'New Back'
        })

        self.assertRedirects(response, reverse('flashcards.index'))
        self.assertTrue(Flashcard.objects.filter(front_text='New Front').exists())

    def test_update_flashcard(self):
        self.client.login(username='testuser', password='password123')

        # Test POST request
        response = self.client.post(reverse('flashcards.update_flashcard'), {
            'card_id': self.flashcard1.id,
            'front_text': 'Updated Front',
            'back_text': 'Updated Back'
        })

        self.assertRedirects(response, reverse('flashcards.index'))
        self.flashcard1.refresh_from_db()
        self.assertEqual(self.flashcard1.front_text, 'Updated Front')
        self.assertEqual(self.flashcard1.back_text, 'Updated Back')

    def test_delete_flashcard(self):
        self.client.login(username='testuser', password='password123')

        # Test POST request
        response = self.client.post(reverse('flashcards.delete_flashcard'), {
            'card_id': self.flashcard1.id
        })

        self.assertRedirects(response, reverse('flashcards.index'))
        self.assertFalse(Flashcard.objects.filter(id=self.flashcard1.id).exists())

    def test_mark_reviewed(self):
        self.client.login(username='testuser', password='password123')
        initial_revisions = self.flashcard1.num_revisions

        # Test POST request
        response = self.client.post(reverse('flashcards.mark_reviewed'), {
            'card_id': self.flashcard1.id
        })

        self.assertRedirects(response, reverse('flashcards.index'))
        self.flashcard1.refresh_from_db()
        self.assertEqual(self.flashcard1.num_revisions, initial_revisions + 1)

    def test_unauthorized_access(self):
        # Create another user
        other_user = User.objects.create_user(username='otheruser', password='password123')
        self.client.login(username='otheruser', password='password123')

        # Try to update another user's flashcard
        response = self.client.post(reverse('flashcards.update_flashcard'), {
            'card_id': self.flashcard1.id,
            'front_text': 'Hacked Front',
            'back_text': 'Hacked Back'
        })

        # Should return 404 because the card_id doesn't match user
        self.assertEqual(response.status_code, 404)
        self.flashcard1.refresh_from_db()
        self.assertNotEqual(self.flashcard1.front_text, 'Hacked Front')