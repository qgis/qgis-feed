# coding=utf-8
""""QGIS News Feed Entry model definition

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-07'
__copyright__ = 'Copyright 2019, ItOpen'

from platform import platform
import re

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.db.models import Q, signals
from django.utils import timezone
from django.utils.translation import gettext as _
import geoip2

from tinymce import models as tinymce_models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from user_visit.models import UserVisit


class QgisLanguageField(models.CharField):
    """
    A language field for Django models.
    """
    def __init__(self, *args, **kwargs):
        # Local import so the languages aren't loaded unless they are needed.
        from .languages import LANGUAGES
        kwargs.setdefault('max_length', 3)
        kwargs.setdefault('choices', LANGUAGES)
        super().__init__(*args, **kwargs)


class PublishedManager(models.Manager):
    """Returns published entries, considering the publication
    dates and the published flag"""

    def get_queryset(self):
        return super().get_queryset().filter(Q(publish_from__isnull=True) | (Q(publish_from__lte=timezone.now())), Q(publish_to__isnull=True) | (Q(publish_to__gte=timezone.now())) , published=True )


class QgisFeedEntry(models.Model):
    """A feed entry for QGIS welcome page
    """

    title = models.CharField(_('Title'), max_length=255)
    image = ProcessedImageField([ResizeToFill(500, 354)], 'JPEG', {'quality': 60}, _('Image'),upload_to='feedimages/%Y/%m/%d/', height_field='image_height', width_field='image_width', max_length=None, blank=True, null=True, help_text=_('Landscape orientation, image will be cropped and scaled automatically to 500x354 px') )
    content = models.TextField()
    url = models.URLField(_('URL'), max_length=200, help_text=_('URL for more information link'))

    # Auto fields
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, editable=False)
    image_height = models.IntegerField(_('Image height'), blank=True, null=True, editable=False)
    image_width = models.IntegerField(_('Image width'), blank=True, null=True, editable=False)
    created = models.DateField(_('Creation date'), auto_now=False, auto_now_add=True, editable=False)
    modified = models.DateField(_('Modification date'), auto_now=True, editable=False)

    # Options
    published = models.BooleanField(_('Published'), default=False, db_index=True)
    sticky = models.BooleanField(_('Sticky entry'), default=False, help_text=_('Check this option to keep this entry on top'))
    sorting = models.PositiveIntegerField(blank=False, null=False, default=0, verbose_name=_('Sorting order'), help_text=_('Increase to show at top of the list'), db_index=True)

    # Filters
    language_filter = QgisLanguageField(_('Language filter'), blank=True, null=True, help_text=_('The entry will be hidden to users who have not set a matching language filter'), db_index=True)
    spatial_filter = models.PolygonField(_('Spatial filter'), blank=True, null=True, help_text=_('The entry will be hidden to users who have set a location that does not match'))

    # Dates
    publish_from = models.DateTimeField(_('Publication start'), auto_now=False, auto_now_add=False, blank=True, null=True, db_index=True)
    publish_to = models.DateTimeField(_('Publication end'), auto_now=False, auto_now_add=False, blank=True, null=True, db_index=True)

    # Managers
    objects = models.Manager()
    published_entries = PublishedManager()

    @property
    def publish_from_epoch(self):
        """Return publish_from as epoch"""

        if self.publish_from is not None:
            return self.publish_from.timestamp()
        return 0

    def __str__(self):
        return self.title

    class Meta:
        db_table = ''
        managed = True
        verbose_name = _('QGIS Feed Entry')
        verbose_name_plural = _('QGIS Feed Entries')
        ordering = ('-sticky', '-sorting', '-publish_from')


class QgisUserVisit(models.Model):
    
    user_visit = models.OneToOneField(
        UserVisit,
        on_delete=models.CASCADE,
        primary_key=True
    )

    location = models.JSONField()

    # Mozilla/5.0 QGIS/32400/Fedora Linux (Workstation Edition)
    qgis_version = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

    platform = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

# Post save user visit signals 
def post_save_user_visit(sender, instance, **kwargs):
    from django.contrib.gis.geoip2 import GeoIP2
    g = GeoIP2()
    country_data = {}
    qgis_version = ''
    platform = ''

    if instance.remote_addr:
        try:
            country_data = g.city(instance.remote_addr)
        except: # AddressNotFoundErrors:
            country_data = {}
        
    version_match = re.search('QGIS(.*)\/', instance.ua_string)

    if version_match:
        qgis_version = version_match.group().replace('QGIS', '').strip('/')
        platform = instance.ua_string[version_match.end():]
    
    if not platform:
        if instance.user_agent:
            platform = instance.user_agent.get_os()

    QgisUserVisit.objects.create(
        user_visit=instance,
        location=country_data,
        qgis_version=qgis_version,
        platform=platform
    )


signals.post_save.connect(post_save_user_visit, sender=UserVisit)
