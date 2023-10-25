# coding=utf-8
""""Tests for QGIS Welcome Page News Feed requests

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-07'
__copyright__ = 'Copyright 2019, ItOpen'

import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import Group, User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from django.core.paginator import Page
from django.urls import reverse

from .models import (
    QgisFeedEntry, QgisUserVisit, DailyQgisUserVisit, aggregate_user_visit_data
)
from .admin import QgisFeedEntryAdmin


class MockRequest:

    def build_absolute_uri(self, uri):
        return uri

class MockSuperUser:

    def is_superuser(self):
        return True

    def has_perm(self, perm):
        return True

class MockStaff:

    def is_superuser(self):
        return False

    def is_staff(self):
        return True

    def has_perm(self, perm):
        return True


request = MockRequest()


class QgisFeedEntryTestCase(TestCase):
    fixtures = ['qgisfeed.json', 'users.json']

    def setUp(self):
        pass

    def test_sorting(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        data[0]['title'] = "Next Microsoft Windows code name revealed"

    def test_unpublished(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in FORTRAN" in titles)

    def test_published(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertTrue("QGIS core will be rewritten in Rust" in titles)

    def test_expired(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in PASCAL" in titles)
        self.assertFalse("QGIS core will be rewritten in GO" in titles)

    def test_future(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in BASIC" in titles)

    def test_lang_filter(self):
        c = Client()
        response = c.get('/?lang=fr')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS acquired by ESRI" in titles)

        c = Client()
        response = c.get('/?lang=en')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertTrue("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS acquired by ESRI" in titles)

    def test_lat_lon_filter(self):
        c = Client()
        response = c.get('/?lat=0&lon=0')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertTrue("Null Island QGIS Meeting" in titles)
        self.assertFalse("QGIS Italian Meeting" in titles)

        response = c.get('/?lat=44.5&lon=9.5')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS Italian Meeting" in titles)

    def test_after(self):
        c = Client()
        response = c.get('/?after=%s' % timezone.datetime(2019, 5, 9).timestamp())
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS Italian Meeting" in titles)

    def test_invalid_parameters(self):
        c = Client()
        response = c.get('/?lat=ZZ&lon=KK')
        self.assertEqual(response.status_code, 400)
        response = c.get('/?lang=KK')
        self.assertEqual(response.status_code, 400)

    def test_image_link(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        image = [d['image'] for d in data if d['image'] != ""][0]
        self.assertEqual(image, "http://testserver/media/feedimages/rust.png" )

    def test_sticky(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        sticky = data[0]
        self.assertTrue(sticky['sticky'])
        not_sticky = data[-1]
        self.assertFalse(not_sticky['sticky'])

    def test_group_is_created(self):
        self.assertEqual(Group.objects.filter(name='qgisfeedentry_authors').count(), 1)
        perms = sorted([p.codename for p in Group.objects.get(name='qgisfeedentry_authors').permissions.all()])
        self.assertEqual(perms, ['add_qgisfeedentry', 'view_qgisfeedentry'])
        # Create a staff user and verify
        staff = User(username='staff_user', is_staff=True)
        staff.save()
        self.assertIsNotNone(staff.groups.get(name='qgisfeedentry_authors'))
        self.assertEqual(staff.get_all_permissions(), set(('qgisfeed.add_qgisfeedentry', 'qgisfeed.view_qgisfeedentry')))

    def test_admin_publish_from(self):
        """Test that published entries have publish_from set"""

        site = AdminSite()
        ma = QgisFeedEntryAdmin(QgisFeedEntry, site)
        obj = QgisFeedEntry(title='Test entry')
        request.user = User.objects.get(username='admin')
        form = ma.get_form(request, obj)
        ma.save_model(request, obj, form, False)
        self.assertIsNone(obj.publish_from)
        self.assertFalse(obj.published)
        obj.published = True
        ma.save_model(request, obj, form, True)
        self.assertIsNotNone(obj.publish_from)
        self.assertTrue(obj.published)

    def test_admin_author_is_set(self):
        site = AdminSite()
        ma = QgisFeedEntryAdmin(QgisFeedEntry, site)
        obj = QgisFeedEntry(title='Test entry 2')
        request.user = User.objects.get(username='staff')
        form = ma.get_form(request, obj)
        ma.save_model(request, obj, form, False)
        self.assertEqual(obj.author, request.user)


class QgisUserVisitTestCase(TestCase):

    def test_user_visit(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        c.get('/')
        user_visit = QgisUserVisit.objects.filter(
            platform__icontains='Fedora Linux (Workstation Edition)')
        self.assertEqual(user_visit.count(), 1)
        self.assertEqual(user_visit.first().qgis_version, '32400')

    def test_ip_address_removed(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)',
                   REMOTE_ADDR='180.247.213.170')
        c.get('/')
        qgis_visit = QgisUserVisit.objects.first()
        self.assertTrue(qgis_visit.user_visit.remote_addr == '')
        self.assertTrue(qgis_visit.location['country_name'] == 'Indonesia')

    def test_aggregate_visit(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/31400/Fedora '
                                   'Linux (Workstation Edition)',
                   REMOTE_ADDR='180.247.213.170')
        c.get('/')
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Windows 10',
                   REMOTE_ADDR='180.247.213.160')
        c.get('/')
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Windows XP',
                   REMOTE_ADDR='180.247.213.160')
        c.get('/')
        aggregate_user_visit_data()
        daily_visit = DailyQgisUserVisit.objects.first()
        self.assertTrue(daily_visit.platform['Windows 10'] == 1)
        self.assertTrue(daily_visit.qgis_version['32400'] == 2)
        self.assertTrue(daily_visit.country['Indonesia'] == 3)


class LoginTestCase(TestCase):
    """
    Test the login feature
    """
    fixtures = ['qgisfeed.json', 'users.json']

    def setUp(self):
        self.client = Client()

    def test_valid_login(self):
        response = self.client.login(username='admin', password='admin')
        self.assertTrue(response)

    def test_invalid_login(self):
        response = self.client.login(username='admin', password='wrongpassword')
        self.assertFalse(response)

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