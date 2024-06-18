from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import Group, User
from django.core.paginator import Page
from django.urls import reverse
from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.core import mail

from ..utils import get_field_max_length

from ..models import (
    CharacterLimitConfiguration, QgisFeedEntry
)

from os.path import join

class FeedsListViewTestCase(TestCase):
    """
    Test the feeds list feature
    """
    fixtures = ['qgisfeed.json', 'users.json']
    def setUp(self):
        self.client = Client()

    def test_authenticated_user_access(self):
        self.client.login(username='admin', password='admin')

        # Access the feeds_list view after logging in
        response = self.client.get(reverse('feeds_list'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'feeds/feeds_list.html')

    def test_unauthenticated_user_redirect_to_login(self):
        # Access the feeds_list view without logging in
        response = self.client.get(reverse('feeds_list'))

        # Check if the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feeds_list'))


    def test_nonstaff_user_redirect_to_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        # Access the feeds_list view with a non staff user
        response = self.client.get(reverse('feeds_list'))

        # Check if the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feeds_list'))

    def test_feeds_list_filtering(self):
        self.client.login(username='admin', password='admin')
        # Simulate a GET request with filter parameters
        data = {
            'title': 'QGIS',
            'author': 'admin',
            'language_filter': 'en',
            'publish_from': '2019-01-01',
            'publish_to': '2023-12-31',
            'sort_by': 'title',
            'order': 'asc',
        }
        response = self.client.get(reverse('feeds_list'), data)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the expected context data
        self.assertTrue('feeds_entry' in response.context)
        self.assertTrue(isinstance(response.context['feeds_entry'], Page))
        self.assertTrue('sort_by' in response.context)
        self.assertTrue('order' in response.context)
        self.assertTrue('current_order' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue('count' in response.context)

class FeedsItemFormTestCase(TestCase):
    """
    Test the feeds add/update feature
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


    def test_authenticated_user_access(self):
        self.client.login(username='admin', password='admin')

        # Access the feed_entry_add view after logging in
        response = self.client.get(reverse('feed_entry_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feeds/feed_item_form.html')
        self.assertTrue('form' in response.context)

        # Check if the approver has the permission. 
        # Here, only the the admin user is listed.
        approvers = response.context['form']['approvers']
        self.assertEqual(len(approvers), 1)
        approver_id = int(approvers[0].data['value'])
        approver = User.objects.get(pk=approver_id)
        self.assertTrue(approver.has_perm("qgisfeed.publish_qgisfeedentry"))

        # Access the feed_entry_update view after logging in
        response = self.client.get(reverse('feed_entry_update', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feeds/feed_item_form.html')
        self.assertTrue('form' in response.context)

    def test_unauthenticated_user_redirect_to_login(self):
        # Access the feed_entry_add view without logging in
        response = self.client.get(reverse('feed_entry_add'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feed_entry_add'))
        self.assertIsNone(response.context)

        # Access the feed_entry_update view without logging in
        response = self.client.get(reverse('feed_entry_update', args=[3]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feed_entry_update', args=[3]))
        self.assertIsNone(response.context)

    def test_nonstaff_user_redirect_to_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Access the feed_entry_add view with a non staff user
        response = self.client.get(reverse('feed_entry_add'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feed_entry_add'))
        self.assertIsNone(response.context)

        # Access the feed_entry_add view with a non staff user
        response = self.client.get(reverse('feed_entry_update', args=[3]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feed_entry_update', args=[3]))
        self.assertIsNone(response.context)

    def test_authenticated_user_add_feed(self):
        # Add a feed entry test
        self.client.login(username='staff', password='staff')

        response = self.client.post(reverse('feed_entry_add'), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))


    def test_authenticated_user_update_feed(self):
        # Update a feed entry test
        self.client.login(username='admin', password='admin')

        response = self.client.post(reverse('feed_entry_update', args=[3]), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))


    def test_not_allowed_user_update_feed(self):
        # Update a feed entry with a non allowed user
        self.client.login(username='staff', password='staff')

        response = self.client.post(reverse('feed_entry_update', args=[7]), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('feed_entry_update', args=[7]))
        self.assertIsNone(response.context)

    def test_allowed_user_publish_feed(self):
        # Publish a feed entry test
        self.client.login(username='admin', password='admin')
        self.post_data['publish'] = 1
        response = self.client.post(reverse('feed_entry_update', args=[7]), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))

        updated_data = QgisFeedEntry.objects.get(pk=7)
        self.assertTrue(updated_data.published)

    def test_allowed_staff_publish_feed(self):
        # Update a feed entry with an allowed staff user
        user = User.objects.get(username='staff')
        user.save()
        group = Group.objects.get(name='qgisfeedentry_approver')
        group.user_set.add(user)

        self.client.login(username='staff', password='staff')
        self.post_data['publish'] = 1
        response = self.client.post(reverse('feed_entry_update', args=[7]), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))

        updated_data = QgisFeedEntry.objects.get(pk=7)
        self.assertTrue(updated_data.published)

    def test_allowed_staff_unpublish_feed(self):
        # Update a feed entry with an allowed staff user
        user = User.objects.get(username='staff')
        user.save()
        group = Group.objects.get(name='qgisfeedentry_approver')
        group.user_set.add(user)

        self.client.login(username='staff', password='staff')
        self.post_data['publish'] = 0

        response = self.client.post(reverse('feed_entry_update', args=[7]), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))

        updated_data = QgisFeedEntry.objects.get(pk=7)
        self.assertFalse(updated_data.published)

    def test_authenticated_user_add_invalid_data(self):
        # Add a feed entry that contains invalid data
        self.client.login(username='staff', password='staff')
        spatial_filter = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        image_path = join(settings.MEDIA_ROOT, "feedimages", "rust.png")

        # Limit content value to 10 characters
        config, created = CharacterLimitConfiguration.objects.update_or_create(
            field_name="content",
            max_characters=10
        )

        post_data = {
            'title': '',
            'image': open(image_path, "rb"),
            'content': '<p>Tired with C++ intricacies, the core developers have decided to rewrite QGIS in <strong>Rust</strong>',
            'url': '',
            'sticky': False,
            'sorting': 0,
            'language_filter': 'en',
            'spatial_filter': str(spatial_filter),
            'publish_from': '',
            'publish_to': ''
        }

        response = self.client.post(reverse('feed_entry_add'), data=post_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('title', form.errors, "This field is required.")
        self.assertIn('content', form.errors, "Ensure this value has at most 10 characters (it has 104).")

    def test_get_field_max_length(self):
        # Test the get_field_max_length function
        content_max_length = get_field_max_length(CharacterLimitConfiguration, field_name="content")
        self.assertEqual(content_max_length, 500)
        CharacterLimitConfiguration.objects.create(
            field_name="content",
            max_characters=1000
        )
        content_max_length = get_field_max_length(CharacterLimitConfiguration, field_name="content")
        self.assertEqual(content_max_length, 1000)

    def test_add_feed_with_reviewer(self):
        # Add a feed entry with specified reviewer test
        self.client.login(username='staff', password='staff')
        self.post_data['reviewers'] = [1]

        response = self.client.post(reverse('feed_entry_add'), data=self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('feeds_list'))

        self.assertEqual(
            mail.outbox[0].recipients(),
            ['me@email.com']
        )

        self.assertEqual(
            mail.outbox[0].from_email,
            settings.QGISFEED_FROM_EMAIL
        )

