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
from django.db import connection

from ..models import (
    QgisFeedEntry
)
from ..admin import QgisFeedEntryAdmin


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
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        data[0]['title'] = "Next Microsoft Windows code name revealed"

    def test_unpublished(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in FORTRAN" in titles)

    def test_published(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertTrue("QGIS core will be rewritten in Rust" in titles)

    def test_expired(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in PASCAL" in titles)
        self.assertFalse("QGIS core will be rewritten in GO" in titles)

    def test_future(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in BASIC" in titles)

    def test_lang_filter(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/?lang=fr')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS acquired by ESRI" in titles)

        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/?lang=en')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertTrue("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS acquired by ESRI" in titles)

    def test_lat_lon_filter(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
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
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/?after=%s' % timezone.datetime(2019, 5, 9).timestamp())
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)
        self.assertTrue("QGIS Italian Meeting" in titles)

        # Check that an updated entry is added to the feed even if
        # expired, but only with QGIS >= 3.36
        with connection.cursor() as cursor:
            cursor.execute("UPDATE qgisfeed_qgisfeedentry SET publish_to='2019-04-09', modified = '2019-05-10', title='Null Island QGIS Hackfest' WHERE title='Null Island QGIS Meeting'")

        response = c.get('/?after=%s' % timezone.datetime(2019, 5, 9).timestamp())
        titles = [d['title'] for d in data]
        self.assertFalse("Null Island QGIS Meeting" in titles)

        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/33600/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/?after=%s' % timezone.datetime(2019, 5, 9).timestamp())
        data = json.loads(response.content)
        null_island = [d for d in data if d['title'] == "Null Island QGIS Hackfest"][0]
        self.assertTrue(timezone.datetime(2019, 5, 9).timestamp() > null_island['publish_to'])


    def test_invalid_parameters(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/?lat=ZZ&lon=KK')
        self.assertEqual(response.status_code, 400)
        response = c.get('/?lang=KK')
        self.assertEqual(response.status_code, 400)

    def test_image_link(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
        response = c.get('/')
        data = json.loads(response.content)
        image = [d['image'] for d in data if d['image'] != ""][0]
        self.assertEqual(image, "http://testserver/media/feedimages/rust.png" )

    def test_sticky(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0 QGIS/32400/Fedora '
                                   'Linux (Workstation Edition)')
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