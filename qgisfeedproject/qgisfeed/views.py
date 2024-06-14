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
from django.conf import settings
from django.utils import timezone
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from django.db import transaction
from django.contrib.auth.models import User

from .forms import FeedEntryFilterForm, FeedItemForm, HomePageFilterForm
from .utils import get_field_max_length, notify_reviewers
from .models import QgisFeedEntry, CharacterLimitConfiguration
from .languages import LANGUAGE_KEYS
import json

from user_visit.models import UserVisit
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


QGISFEED_MAX_RECORDS=getattr(settings, 'QGISFEED_MAX_RECORDS', 20)

# Decorator
staff_required = user_passes_test(lambda u: u.is_staff)

class BadRequestException(Exception):
    pass

class QgisEntriesView(View):
    """Views for QGIS Welcome Page News Feed, returns JSON data

    accepted filters:
    - lang=[2 letter iso code for the language]
    """

    form_class = HomePageFilterForm
    template_name = 'feeds/feed_home_page.html'

    def get_filters(self, request):
        """Extract filters from the request and checks validity

        :param request: the HTTP request
        :type request: Django HTTPRequest
        :return: a dictionary with lang and location (WKT Point) parameters
        :rtype: dict
        """
        filters = {}
        if request.GET.get('lang'):
            lang = request.GET.get('lang')
            if not lang in LANGUAGE_KEYS:
                raise BadRequestException("Invalid language parameter.")
            filters['lang'] = lang
        if request.GET.get('lat') and request.GET.get('lon'):
            try:
                location = 'point(%s %s)' % (request.GET.get('lon'), request.GET.get('lat'))
                GEOSGeometry(location)
                filters['location'] = location
            except ValueError:
                raise BadRequestException("Invalid lat/lon parameters.")

        if request.GET.get('publish_from'):
            try:
                filters['after'] = timezone.make_aware(
                    timezone.datetime.strptime(
                        request.GET.get('publish_from'), "%Y-%m-%d"
                        )
                )
            except ValueError:
                raise BadRequestException("Invalid after parameter.")

        if request.GET.get('after') is not None:
            try:
                filters['after'] = timezone.make_aware(timezone.datetime.fromtimestamp(float(request.GET.get('after'))))
            except ValueError:
                raise BadRequestException("Invalid after parameter.")


        return filters


    def get(self, request):
        form = self.form_class(request.GET)
        data = []

        try:
            filters = self.get_filters(request)
        except BadRequestException as ex:
            return HttpResponseBadRequest("%s" % ex)

        user_agent = request.META.get('HTTP_USER_AGENT')
        qgis_version = None
        if "QGIS/" in str(user_agent):
            try:
                qgis_pos = user_agent.find('QGIS/')
                if qgis_pos >= 0:
                    qgis_version = int(int(user_agent[qgis_pos + 5: qgis_pos + 10]))
            except ValueError:
                pass

        # "after" is only set by QGIS client on requests after the first one.
        # The logic here is for QGIS >= 3.36 to send anything "published=True"
        # that has been modified since the last feed check, we also need to
        # send expired items because setting the "publish_to" publication end
        # time in the past is the way to remove them from the cient cache and
        # because entries might have been updated.
        # For older QGIS < 3.36 we only send published items, optionally filtered
        # by >= `after`.

        after = filters.get('after')
        if after is None:
            qs = QgisFeedEntry.published_entries.all()
        else:
            # For update capabilities require QGIS >= 3.36
            if qgis_version is None or qgis_version < 33600:
                qs = QgisFeedEntry.published_entries.all()
                qs = qs.filter(publish_from__gte=filters.get('after'))
            else:  # fallback to original behavior for QGIS < 3.36
                qs = QgisFeedEntry.objects.all()
                qs = qs.filter(modified__gte=after, published=True)

        # Get filters for lang and lat/lon
        if filters.get('lang') is not None:
            qs = qs.filter(Q(language_filter__isnull=True) | Q(language_filter=filters.get('lang')))

        if filters.get('location') is not None:
            qs = qs.filter(spatial_filter__contains=filters.get('location'))

        for record in qs.values('pk', 'publish_from', 'publish_to', 'title','image', 'content', 'url', 'sticky')[:QGISFEED_MAX_RECORDS]:
            if record['publish_from']:
                record['publish_from'] = record['publish_from'].timestamp()
            if record['publish_to']:
                record['publish_to'] = record['publish_to'].timestamp()
            if record['image']:
                record['image'] = request.build_absolute_uri(settings.MEDIA_URL + record['image'])
            data.append(record)

        data_json = json.dumps(data, indent=(2 if settings.DEBUG else 0))
        if "qgis" in str(user_agent).lower() or request.GET.get('json', '') == '1':
            return HttpResponse(data_json,content_type='application/json')
        else:
            args = {
                "data": data,
                "form": form,
                "data_json": json.dumps(data, indent=2)
            }
            return render(request, self.template_name, args)

@method_decorator(staff_required, name='dispatch')
@method_decorator(permission_required('qgisfeed.view_qgisfeedentry'), name='dispatch')
class FeedsListView(View):
    """
    List of feeds
    This view renders a paginated, sorted according
    to the request parameters list of feeds
    """
    form_class = FeedEntryFilterForm
    template_name = 'feeds/feeds_list.html'
    items_per_page = 15  # Set the number of items per page

    def get(self, request):
        form = self.form_class(request.GET)
        feeds_entry = QgisFeedEntry.objects.all()

        # Get filter parameters from the query string
        if form.is_valid():
            title = form.cleaned_data.get('title')
            if title:
                feeds_entry = feeds_entry.filter(title__icontains=title)

            author = form.cleaned_data.get('author')
            if author:
                feeds_entry = feeds_entry.filter(author__username__icontains=author)

            language_filter = form.cleaned_data.get('language_filter')
            if language_filter:
                feeds_entry = feeds_entry.filter(language_filter=language_filter)

            publish_from = form.cleaned_data.get('publish_from')
            if publish_from:
                feeds_entry = feeds_entry.filter(publish_from__gt=publish_from)

            publish_to = form.cleaned_data.get('publish_to')
            if publish_to:
                feeds_entry = feeds_entry.filter(publish_to__lt=publish_to)

            need_review = form.cleaned_data.get('need_review')
            if need_review:
                published = not bool(int(need_review))
                feeds_entry = feeds_entry.filter(published=published)

        # Get sorting parameters from the query string
        sort_by = request.GET.get('sort_by', 'publish_from')
        current_order = request.GET.get('order', 'desc')

        if current_order == 'asc':
            feeds_entry = feeds_entry.order_by(sort_by)
            next_order = 'desc'
        else:
            next_order = 'asc'
            feeds_entry = feeds_entry.order_by(f'-{sort_by}')

        # Get the count of all/filtered entries
        count = feeds_entry.count()

        # Paginate the list of feeds
        page = request.GET.get('page', 1)
        paginator = Paginator(feeds_entry, self.items_per_page)

        try:
            feeds_entry = paginator.page(page)
        except PageNotAnInteger:
            feeds_entry = paginator.page(1)
        except EmptyPage:
            feeds_entry = paginator.page(paginator.num_pages)

        user = request.user
        user_can_add = user.has_perm("qgisfeed.add_qgisfeedentry")
        user_can_change = user.has_perm("qgisfeed.change_qgisfeedentry")

        return render(
            request,
            self.template_name,
            {
                "feeds_entry": feeds_entry,
                "sort_by": sort_by,
                "order": next_order,
                "current_order": current_order,
                "form": form,
                "count": count,
                "user_can_change": user_can_change,
                "user_can_add": user_can_add,
            },
        )


@method_decorator(staff_required, name='dispatch')
@method_decorator(permission_required('qgisfeed.add_qgisfeedentry'), name='dispatch')
class FeedEntryAddView(View):
    """
    View to add a feed entry item
    """
    form_class = FeedItemForm
    template_name = 'feeds/feed_item_form.html'

    def get(self, request):
        msg = None
        success = False
        user = request.user
        user_is_approver = user.has_perm("qgisfeed.publish_qgisfeedentry")
        form = self.form_class()

        args = {
            "form": form,
            "msg": msg,
            "success": success,
            "published": False,
            "user_is_approver": user_is_approver,
            "content_max_length": get_field_max_length(CharacterLimitConfiguration, field_name="content")
        }

        return render(request, self.template_name, args)

    def post(self, request):
        msg = None
        success = False
        user = request.user
        user_is_approver = user.has_perm("qgisfeed.publish_qgisfeedentry")
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                new_object = form.save(commit=False)
                new_object.set_request(request)  # Pass the 'request' to get the user in the model
                new_object.save()
                success = True

                # If at least one reviewer is specified, 
                # set the specified reviewers as recipients 
                # and cc the other reviewers. 
                # Otherwise, send the email to all reviewers.
                reviewers = User.objects.filter(
                    is_active=True, 
                    email__isnull=False
                ).exclude(email='')

                recipients = [
                    u.email for u in reviewers if u.has_perm("qgisfeed.publish_qgisfeedentry")
                ]
                cc_list = []
                if form.cleaned_data.get("approvers") and len(form.cleaned_data.get("approvers")) > 0:
                    approver_ids = form.cleaned_data.get("approvers")
                    recipients = [
                        u.email for u in reviewers.filter(
                            pk__in=approver_ids
                        ) if u.has_perm("qgisfeed.publish_qgisfeedentry")
                    ]
                    cc_list = [
                        u.email for u in reviewers.exclude(pk__in=approver_ids) if u.has_perm("qgisfeed.publish_qgisfeedentry")
                    ]

                if recipients and len(recipients) > 0:
                    notify_reviewers(request.user, request, recipients, cc_list, new_object)

                return redirect('feeds_list')
        else:
            success = False
            msg = "Form is not valid"


        args = {
            "form": form,
            "msg": msg,
            "success": success,
            "published": False,
            "user_is_approver": user_is_approver,
            "content_max_length": get_field_max_length(CharacterLimitConfiguration, field_name="content")
        }

        return render(request, self.template_name, args)

@method_decorator(staff_required, name='dispatch')
@method_decorator(permission_required('qgisfeed.change_qgisfeedentry'), name='dispatch')
class FeedEntryUpdateView(View):
    """
    View to update/publish a feed entry item
    """
    form_class = FeedItemForm
    template_name = 'feeds/feed_item_form.html'

    def get(self, request, pk):
        msg = None
        success = False
        feed_entry = get_object_or_404(QgisFeedEntry, pk=pk)
        user = request.user
        user_is_approver = user.has_perm("qgisfeed.publish_qgisfeedentry")
        form = self.form_class(instance=feed_entry)
        args = {
            "form": form,
            "msg": msg,
            "success": success,
            "published": feed_entry.published,
            "user_is_approver": user_is_approver,
            "content_max_length": get_field_max_length(CharacterLimitConfiguration, field_name="content")
        }

        return render(request, self.template_name, args)

    def post(self, request, pk):
        msg = None
        success = False
        feed_entry = get_object_or_404(QgisFeedEntry, pk=pk)
        user = request.user
        user_is_approver = user.has_perm("qgisfeed.publish_qgisfeedentry")
        form = self.form_class(request.POST, request.FILES, instance=feed_entry)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('publish') and user_is_approver:
                try:
                    publish = bool(int(request.POST.get('publish')))
                    instance.published = publish
                except ValueError:
                    pass

            instance.save()
            success = True
            return redirect('feeds_list')
        else:
            success = False
            msg = "Form is not valid"
        args = {
            "form": form,
            "msg": msg,
            "success": success,
            "published": feed_entry.published,
            "user_is_approver": user_is_approver,
            "content_max_length": get_field_max_length(CharacterLimitConfiguration, field_name="content")
        }

        return render(request, self.template_name, args)
