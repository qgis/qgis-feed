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

from .models import QgisFeedEntry

# Get an instance of a logger
logger = logging.getLogger(__name__)

QGISFEED_FROM_EMAIL = getattr(settings, 'QGISFEED_FROM_EMAIL', 'noreply@qgis.org')

class QgisFeedEntryAdmin(admin.GeoModelAdmin):

    list_display = ('title', 'author', 'language_filter', 'published',
                    'publication_start', 'publication_end', 'sorting')

    def notify(self, author, recipients, obj):
        """Send notification emails"""
        body = """
            User %s added a new entry.\r\n
            Title: %s\r\n
            Link: %s\r\n
            """ % (
                author.username,
                obj.title,
                reverse('admin:qgisfeed_qgisfeedentry_change', args=(obj.pk,))
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
        obj.save()

        if not change and not request.user.is_superuser:
            recipients = [u.email for u in User.objects.filter(is_superuser=True, is_active=True, email__isnull=False).exclude(email='')]
            if recipients:
                self.notify(request.user, recipients, obj)


    def get_form(self, request, obj=None, **kwargs):
        """Hide published from not admin users"""

        if not request.user.is_superuser:
            self.exclude = ("published", "sorting")
        form = super(QgisFeedEntryAdmin, self).get_form(request, obj, **kwargs)
        return form


admin.site.register(QgisFeedEntry, QgisFeedEntryAdmin)
