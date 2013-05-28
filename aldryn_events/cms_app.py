# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url, patterns

from cms.apphook_pool import apphook_pool
from cms.app_base import CMSApp

from .views import (
    EventListView,
    EventDetailView,
    ResetEventRegistration
)


class EventListAppHook(CMSApp):
    name = _('Event Listing')
    urls = [
        patterns('',
            url(r'^$', EventListView.as_view(), name='events_list'),
            url(r'^(?P<year>\d{4})/$', EventListView.as_view(), name='events_list-by-year'),
            url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', EventListView.as_view(), name='events_list-by-month'),
            url(r'^archive/$', EventListView.as_view(archive=True), name='events_list_archive'),
            url(r'^archive/(?P<year>\d{4})/$', EventListView.as_view(archive=True), name='events_list_archive-by-year'),
            url(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$', EventListView.as_view(archive=True), name='events_list_archive-by-month'),
            url(r'^(?P<slug>[\w_-]+)/$', EventDetailView.as_view(), name='events_detail'),
            url(r'^(?P<slug>[\w_-]+)/reset/$', ResetEventRegistration.as_view(), name='events_registration_reset'),
        )
    ]
apphook_pool.register(EventListAppHook)

