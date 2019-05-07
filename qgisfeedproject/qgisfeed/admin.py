# coding=utf-8
""""QGIS Welcome Page Entry admin

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-07'
__copyright__ = 'Copyright 2019, ItOpen'


# Register your models here.

from django.contrib.gis import admin
from .models import QgisFeedEntry


class QgisFeedEntryAdmin(admin.GeoModelAdmin):

    list_display = ('title', 'author', 'language_filter', 'published', 'publication_start', 'publication_end', 'sorting')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()

admin.site.register(QgisFeedEntry, QgisFeedEntryAdmin)
