# coding=utf-8
""""Views for QGIS Welcome Page News Feed, returns JSON data

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-07'
__copyright__ = 'Copyright 2019, ItOpen'


from django.core.serializers import serialize
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.db.models import Q
from .models import QgisFeedEntry
from .languages import LANGUAGE_KEYS
import json

class BadRequestException(Exception):
    pass

class QgisEntriesView(View):
    """Views for QGIS Welcome Page News Feed, returns JSON data

    accepted filters:
    - lang=[2 letter iso code for the language]
    """

    def get_filters(self, request):
        """Extract filters from the request and checks validity

        :param request: the HTTP request
        :type request: Django HTTPRequest
        :return: a dictionary with lang and location (WKT Point) parameters
        :rtype: dict
        """
        filters = {}
        if request.GET.get('lang') is not None:
            lang = request.GET.get('lang')
            if not lang in LANGUAGE_KEYS:
                raise BadRequestException("Invalid language parameter.")
            filters['lang'] = lang
        if request.GET.get('lat') is not None and request.GET.get('lon') is not None:
            try:
                location = 'point(%s %s)' % (request.GET.get('lon'), request.GET.get('lat'))
                GEOSGeometry(location)
                filters['location'] = location
            except ValueError:
                raise BadRequestException("Invalid lat/lon parameters.")
        return filters


    def get(self, request):
        data = []
        qs = QgisFeedEntry.published_entries.all()

        try:
            filters = self.get_filters(request)
        except BadRequestException as ex:
            return HttpResponseBadRequest("%s" % ex)

        # Get filters for lang and lat/lon
        if filters.get('lang') is not None:
            qs = qs.filter(Q(language_filter__isnull=True) | Q(language_filter=filters.get('lang')))

        if filters.get('location') is not None:
            qs = qs.filter(spatial_filter__contains=filters.get('location'))

        for record in qs.values('title','image', 'content', 'url'):
            data.append(record)

        return HttpResponse(json.dumps(data), content_type='application/json')



