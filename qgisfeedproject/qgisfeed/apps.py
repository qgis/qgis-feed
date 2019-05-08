# coding=utf-8
""""Configure QGIS News app, create user group and signals

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-08'
__copyright__ = 'Copyright 2019, ItOpen'


from django.apps import AppConfig
from django.db.models.signals import post_save


class QgisFeedConfig(AppConfig):
    name = 'qgisfeed'

    def ready(self):
        from .signals import setup_group
        from django.contrib.auth.models import User
        post_save.connect(setup_group, sender=User)

