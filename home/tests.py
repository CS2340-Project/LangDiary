from django.test import TestCase
from django.urls import reverse


class HomeViewsTests(TestCase):
    def test_index_view(self):
        """Test index view returns correct response with proper template and context"""
        response = self.client.get(reverse('home.index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertEqual(response.context['template_data']['title'], 'LangDiary - Home')

    def test_about_view(self):
        """Test about view returns correct response with proper template and context"""
        response = self.client.get(reverse('home.about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/about.html')
        self.assertEqual(response.context['template_data']['title'], 'LangDiary - About')