# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

urlpatterns = patterns('aldryn_events.views',  # NOQA
    url(r'^$', 'event_list', name='events_list'),
    url(r'^get-dates/$', 'event_dates', name='get-calendar-dates'),
    url(r'^get-dates/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        'event_dates', name='get-calendar-dates'),
    url(r'^(?P<year>\d{4})/$', 'event_list', name='events_list-by-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'event_list',
        name='events_list-by-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        'event_list', name='events_list-by-day'),
    url(r'^archive/$', 'event_list_archive', name='events_list_archive'),
    url(r'^archive/(?P<year>\d{4})/$', 'event_list_archive',
        name='events_list_archive-by-year'),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'event_list_archive',
        name='events_list_archive-by-month'),
    url(r'^(?P<slug>[\w_-]+)/$', 'event_detail', name='events_detail'),
    url(r'^(?P<slug>[\w_-]+)/reset/$', 'reset_event_registration',
        name='events_registration_reset'),
)
