# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import override

from cms import api
from cms.utils.i18n import force_language

from aldryn_events.models import Event

from .base import EventBaseTestCase, tz_datetime


class TestEventViews(EventBaseTestCase):

    def setUp(self):
        super(TestEventViews, self).setUp()
        root_page = self.create_root_page()
        page = api.create_page(
            'Events en', self.template, 'en', published=True, parent=root_page,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 8)
        )
        api.create_title('de', 'Events de', page)
        page.publish('en')
        page.publish('de')
        page.reload()
        # aldryn apphook reload needs some time to reload test
        # server implementation so we will provide some time for him
        # otherwise test_event_detail_view is too quick, and fails.
        with override('en'):
            page_url = page.get_absolute_url()
        self.client.get(page_url)

    def get_past_date(self, days=2):
        now_date = datetime.datetime.now().date()
        return now_date - datetime.timedelta(days=days)

    def get_new_past_event_data(
            self, start_date=None, end_date=None, arg_list=None):
        if start_date is None:
            start_date = self.get_past_date()
        if end_date is None:
            end_date = self.get_past_date()
        if arg_list is None:
            arg_list = ('day', 'month', 'year')
        dates = {
            'start_date': start_date,
            'end_date': end_date,
        }
        event_data = self.make_default_values_with_new_dates(
            date_values=dates)
        kwargs = {}
        for att_name in arg_list:
            kwargs[att_name] = getattr(start_date, att_name)
        return event_data, kwargs

    def test_event_list_view_returns_200(self):
        url = reverse("{0}:events_list".format(self.app_config.namespace))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_event_list_by_day_past_event_1_day_long(self):
        """
        Regression test case for checking that if event was created
        today but for past day it is still displayed on list view for day
        """
        event_data, kwargs = self.get_new_past_event_data()
        with force_language('en'):
            event = self.create_event(**event_data)
            event_url = event.get_absolute_url()
            view_url = reverse('{0}:events_list-by-day'.format(
                self.app_config.namespace), kwargs=kwargs)
        response = self.client.get(view_url)
        self.assertContains(response, event.get_title())
        self.assertContains(response, event_url)

    def test_event_list_by_month_past_event_1_day_long(self):
        """
        Regression test case for checking that if event was created
        today but for past date it is still displayed on month list view
        """
        # make it previous month or so
        start_date = end_date = self.get_past_date(35)
        event_data, kwargs = self.get_new_past_event_data(
            start_date, end_date, arg_list=('month', 'year'))
        with force_language('en'):
            event = self.create_event(**event_data)
            event_url = event.get_absolute_url()
            view_url = reverse('{0}:events_list-by-month'.format(
                self.app_config.namespace), kwargs=kwargs)
        response = self.client.get(view_url)
        self.assertContains(response, event.get_title())
        self.assertContains(response, event_url)

    def test_event_list_by_year_past_event_1_day_long(self):
        """
        Regression test case for checking that if event was created
        today but for past date it is still displayed on month list view
        """
        # make it previous year or so
        start_date = end_date = self.get_past_date(366)
        event_data, kwargs = self.get_new_past_event_data(
            start_date, end_date, arg_list=('year',))
        with force_language('en'):
            event = self.create_event(**event_data)
            event_url = event.get_absolute_url()
            view_url = reverse('{0}:events_list-by-year'.format(
                self.app_config.namespace), kwargs=kwargs)
        response = self.client.get(view_url)
        self.assertContains(response, event.get_title())
        self.assertContains(response, event_url)

    def test_event_detail_view(self):
        with override("en"):
            event = Event.objects.create(**{
                'title': 'MyEvent',
                'slug': 'my-event',
                'start_date': tz_datetime(2015, 6, 1),
                'end_date': tz_datetime(2015, 7, 1),
                'app_config': self.app_config,
                'is_published': True,
            })
        url = event.get_absolute_url(language="en")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
