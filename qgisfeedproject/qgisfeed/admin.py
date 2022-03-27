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

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from user_visit.admin import UserVisitAdmin
from user_visit.models import UserVisit

from .models import QgisFeedEntry, QgisUserVisit

# Get an instance of a logger
logger = logging.getLogger('qgisfeed.admin')

QGISFEED_FROM_EMAIL = getattr(settings, 'QGISFEED_FROM_EMAIL', 'noreply@qgis.org')

class QgisFeedEntryAdmin(admin.GeoModelAdmin):

    list_display = ('title', 'author', 'language_filter', 'published',
                    'publish_from', 'publish_to', 'sorting')

    def notify(self, author, request, recipients, obj):
        """Send notification emails"""
        body = """
            User %s added a new entry.\r\n
            Title: %s\r\n
            Link: %s\r\n
            """ % (
                author.username,
                obj.title,
                request.build_absolute_uri(reverse('admin:qgisfeed_qgisfeedentry_change', args=(obj.pk,)))
            )
        if settings.DEBUG:
            logger.debug("DEBUG is True: email not sent:\n %s" % body)
        else:
            send_mail(
                'A QGIS News Entry was added: %s' % obj.title,
                body,
                QGISFEED_FROM_EMAIL,
                recipients,
                fail_silently=True
            )

    def save_model(self, request, obj, form, change):
        """Auto-set author and notify superadmin when entry is added"""

        if not change:
            obj.author = request.user

        if obj.publish_from is None and obj.published:
            obj.publish_from = timezone.now()

        obj.save()

        if not change and not request.user.is_superuser:
            recipients = [u.email for u in User.objects.filter(is_superuser=True, is_active=True, email__isnull=False).exclude(email='')]
            if recipients:
                self.notify(request.user, request, recipients, obj)


    def get_form(self, request, obj=None, **kwargs):
        """Hide published from not admin users"""

        if not request.user.is_superuser:
            self.exclude = ("published", "sorting")
        form = super(QgisFeedEntryAdmin, self).get_form(request, obj, **kwargs)
        return form


class QgisUserVisitAdmin(admin.StackedInline):
    readonly_fields = ('qgis_version', 'location', 'platform')
    can_delete = False
    model = QgisUserVisit
   

class UpdatedUserVisitAdmin(UserVisitAdmin):
    inlines = [
        QgisUserVisitAdmin
    ]
    list_display = ("timestamp", "qgis_version", "country", "platform")
    search_fields = (
        "qgisuservisit__qgis_version",
        "qgisuservisit__location"
    )
    readonly_fields = (
        "timestamp",
        "hash",
        "session_key",
        "user_agent",
        "ua_string",
        "created_at",
    )
    exclude = ['user', 'remote_addr']

    def qgis_version(self, obj):
        qgis_version = ''
        if obj.qgisuservisit:
            qgis_version = obj.qgisuservisit.qgis_version
        if not qgis_version:
            qgis_version = '-'
        return qgis_version
    
    def country(self, obj):
        country = '-'
        if obj.qgisuservisit:
            if obj.qgisuservisit.location and 'country_name' in obj.qgisuservisit.location:
                country = obj.qgisuservisit.location['country_name']
        return country

    def platform(sel, obj):
        platfrom_string = 'Unknown'
        if obj.qgisuservisit:
            platfrom_string = obj.qgisuservisit.platform
        return platfrom_string

    qgis_version.short_description = 'QGIS Version'


admin.site.register(QgisFeedEntry, QgisFeedEntryAdmin)
admin.site.unregister(UserVisit)
admin.site.register(UserVisit, UpdatedUserVisitAdmin)
