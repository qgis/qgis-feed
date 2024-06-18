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

from ..models import (
    QgisUserVisit, DailyQgisUserVisit, aggregate_user_visit_data
)


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
        self.assertTrue(daily_visit.country['ID'] == 3)

