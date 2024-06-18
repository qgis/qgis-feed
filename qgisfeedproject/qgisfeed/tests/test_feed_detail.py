# tests.py
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ..models import QgisFeedEntry
from ..views import FeedEntryDetailView
from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.test import Client
from os.path import join

class FeedEntryDetailViewTestCase(TestCase):
    """
    Test feed detail page web version
    """
    fixtures = ['qgisfeed.json', 'users.json']
    def setUp(self):
        self.client = Client()
        spatial_filter = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        image_path = join(settings.MEDIA_ROOT, "feedimages", "rust.png")
        self.post_data = {
            'title': 'QGIS core will be rewritten in Rust',
            'image': open(image_path, "rb"),
            'content': '<p>Tired with C++ intricacies, the core developers have decided to rewrite QGIS in <strong>Rust</strong>',
            'url': 'https://www.null.com',
            'sticky': False,
            'sorting': 0,
            'language_filter': 'en',
            'spatial_filter': str(spatial_filter),
            'publish_from': '2023-10-18 14:46:00+00',
            'publish_to': '2023-10-29 14:46:00+00'
        }
        # Add a feed entry test
        self.client.login(username='staff', password='staff')

        self.client.post(reverse('feed_entry_add'), data=self.post_data)

        self.entry = QgisFeedEntry.objects.last()

        self.factory = RequestFactory()

    def test_feed_entry_detail_view(self):
        url = reverse('feed_entry_detail', kwargs={'pk': self.entry.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feeds/feed_item_detail.html')
        self.assertEqual(response.context['feed_entry'], self.entry)
        self.assertIsNotNone(response.context['spatial_filter_geojson'])

    def test_feed_entry_detail_view_not_found(self):
        url = reverse('feed_entry_detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
