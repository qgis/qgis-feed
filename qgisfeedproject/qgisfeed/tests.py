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


from django.test import TestCase
from django.test import Client
# Create your tests here.
import json

from .models import QgisFeedEntry

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
        self.assertTrue("QGIS core will be rewritten in PASCAL" in titles)

    def test_expired(self):
        c = Client()
        response = c.get('/')
        data = json.loads(response.content)
        titles = [d['title'] for d in data]
        self.assertFalse("QGIS core will be rewritten in Rust" in titles)
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

    def test_invalid_parameters(self):
        c = Client()
        response = c.get('/?lat=ZZ&lon=KK')
        self.assertEqual(response.status_code, 400)
        response = c.get('/?lang=KK')
        self.assertEqual(response.status_code, 400)

