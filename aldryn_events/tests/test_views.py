# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import override

from cms import api
from cms.utils.i18n import force_language

from aldryn_events.models import Event
from aldryn_events.cms_appconfig import EventsConfig

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

        self.list_view_year_month = ('2015', '02')

    def setup_calendar_events(self):
        """
        Create events to check per date list view rendering.
        :return: list of Event objects.
        """
        other_config = EventsConfig.objects.create(namespace='other')
        ev0 = self.create_event(
            title='Start in, end in',
            start_date=tz_datetime(2015, 2, 1),
            end_date=tz_datetime(2015, 2, 10),
            publish_at=tz_datetime(2015, 2, 1)
        )
        ev1 = self.create_event(
            title='Start in, end greater',
            start_date=tz_datetime(2015, 2, 15),
            end_date=tz_datetime(2015, 4, 27),
            publish_at=tz_datetime(2015, 2, 10)
        )

        ev2 = self.create_event(
            title='Start less, end in',
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 2, 15),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev3 = self.create_event(
            title='Start less, end is Null',
            start_date=tz_datetime(2015, 1, 1),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev4 = self.create_event(
            title='Future, end is Null',
            start_date=tz_datetime(2015, 10, 1),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev5 = self.create_event(
            title='Ended event',
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 1, 2),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev6 = self.create_event(
            title='Past ended event',
            start_date=tz_datetime(2013, 1, 1),
            end_date=tz_datetime(2013, 1, 2),
            publish_at=tz_datetime(2013, 1, 1)
        )
        self.create_event(
            title='Other config, start in, end is Null',
            start_date=tz_datetime(2015, 2, 18),
            publish_at=tz_datetime(2015, 2, 10),
            app_config=other_config
        )
        return [ev0, ev1, ev2, ev3, ev4, ev5, ev6]

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
            kwargs[att_name] = getattr(start_date, att_name, None)
        return event_data, kwargs

    def get_list_view_kwargs(self, year, month, day=None):
        """
        Builds the kwarg dict for events list view
        :return: dict
        """
        date_dict = {
            'year': year,
            'month': month
        }
        if day is not None:
            date_dict['day'] = day
        return date_dict

    def response_contains(self, response, indexes, event_list, event_urls):
        """
        Perform multiple self.assertContains against response using indexes
        and checking that response contains event title and event url
        :param response: self.client.get() HttpResponse
        :param indexes: list of integers to get correct item from event_list
        :param event_list: list of event objects
        :param event_urls: list of event urls, should be in the same order as
                           event_list
        :return: None, assertion error would rise if something wrong
        """
        for index in indexes:
            self.assertContains(response, event_list[index].get_title())
            self.assertContains(response, event_urls[index])

    def response_not_contains(self, response, indexes, event_list, event_urls):
        """
        Perform multiple self.assertContains against response using indexes
        and checking that response contains event title and event url
        :param response: self.client.get() HttpResponse
        :param indexes: list of integers to get correct item from event_list
        :param event_list: list of event objects
        :param event_urls: list of event urls, should be in the same order as
                           event_list
        :return: None, assertion error would rise if something wrong
        """
        for index in indexes:
            self.assertNotContains(response, event_list[index].get_title())
            self.assertNotContains(response, event_urls[index])

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

    def test_list_view_by_day_output(self):
        # prepare events
        events_list = self.setup_calendar_events()
        # (start less, end in) and (start in, end in)
        # + out of calendar events (active)
        kwargs1 = self.get_list_view_kwargs(*self.list_view_year_month,
                                            day='1')
        # (start in, end greater) and (start less, end in)
        # + out of calendar events (active)
        kwargs2 = self.get_list_view_kwargs(*self.list_view_year_month,
                                            day='15')
        # includes ev1 + out of calendar events (active)
        kwargs3 = self.get_list_view_kwargs(*self.list_view_year_month,
                                            day='16')
        # Should not contain events from other namespace, but should contain
        # out of calendar events (active)
        kwargs4 = self.get_list_view_kwargs(*self.list_view_year_month,
                                            day='18')

        view_name = '{0}:events_list-by-day'.format(self.app_config.namespace)
        with force_language('en'):
            events_urls = [event.get_absolute_url() for event in events_list]
            view_url1 = reverse(view_name, kwargs=kwargs1)
            view_url2 = reverse(view_name, kwargs=kwargs2)
            view_url3 = reverse(view_name, kwargs=kwargs3)
            view_url4 = reverse(view_name, kwargs=kwargs4)

        response1 = self.client.get(view_url1)
        self.response_contains(
            response1, [0, 2], events_list, events_urls)
        self.response_not_contains(response1, [3], events_list, events_urls)
        # ensure response does not contains past ended event
        self.assertNotContains(response1, events_list[6].get_title())
        self.assertNotContains(response1, events_urls[6])

        response2 = self.client.get(view_url2)
        # should contain event 2 event 3 and event 4
        self.response_contains(
            response2, [1, 2], events_list, events_urls)
        # ensure does not contains invalid events
        self.response_not_contains(
            response2, [0, 4, 5, 6], events_list, events_urls)

        response3 = self.client.get(view_url3)
        self.response_contains(
            response3, [1], events_list, events_urls)

        # ensure does not contains invalid events
        self.response_not_contains(
            response3, [0, 2, 4, 5, 6], events_list, events_urls)

        response4 = self.client.get(view_url4)
        self.response_contains(
            response4, [1], events_list, events_urls)

        # ensure does not contains invalid events
        self.response_not_contains(
            response4, [0, 2, 4, 5, 6], events_list, events_urls)

    def test_list_view_by_month_output(self):
        # prepare events
        events_list = self.setup_calendar_events()

        kwargs1 = self.get_list_view_kwargs(*self.list_view_year_month)
        kwargs2 = self.get_list_view_kwargs('2014', '01')
        kwargs3 = self.get_list_view_kwargs('2015', '11')

        view_name = '{0}:events_list-by-month'.format(
            self.app_config.namespace)
        with force_language('en'):
            events_urls = [event.get_absolute_url() for event in events_list]
            view_url1 = reverse(view_name, kwargs=kwargs1)
            view_url2 = reverse(view_name, kwargs=kwargs2)
            view_url3 = reverse(view_name, kwargs=kwargs3)

        response1 = self.client.get(view_url1)
        # should contain all event valid event cases
        self.response_contains(
            response1, [0, 1, 2], events_list, events_urls)

        # ensure does not contains invalid events
        self.response_not_contains(
            response1, [4, 5, 6], events_list, events_urls)

        response2 = self.client.get(view_url2)
        # shouldn't contain any of the above
        self.response_not_contains(
            response2, range(len(events_list)), events_list, events_urls)

        response3 = self.client.get(view_url3)
        # should not contain events with no end
        self.response_not_contains(
            response3, [3, 4], events_list, events_urls)

        # ensure does not contains invalid events
        self.response_not_contains(
            response3, [0, 1, 2, 5, 6], events_list, events_urls)

    def test_list_view_by_year_output(self):
        # prepare events
        other_config = EventsConfig.objects.create(namespace='other')
        ev0 = self.create_event(
            title='Start in, end in',
            start_date=tz_datetime(2015, 2, 1),
            end_date=tz_datetime(2015, 2, 10),
            publish_at=tz_datetime(2015, 2, 1)
        )
        ev1 = self.create_event(
            title='Start in, end greater',
            start_date=tz_datetime(2015, 2, 15),
            end_date=tz_datetime(2016, 4, 27),
            publish_at=tz_datetime(2015, 2, 10)
        )

        ev2 = self.create_event(
            title='Start less, end in',
            start_date=tz_datetime(2014, 1, 1),
            end_date=tz_datetime(2015, 2, 15),
            publish_at=tz_datetime(2014, 1, 1)
        )
        ev3 = self.create_event(
            title='Start less, end is Null',
            start_date=tz_datetime(2014, 1, 1),
            publish_at=tz_datetime(2014, 1, 1)
        )
        ev4 = self.create_event(
            title='Future, end is Null',
            start_date=tz_datetime(2016, 10, 1),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev5 = self.create_event(
            title='Ended event',
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 1, 2),
            publish_at=tz_datetime(2015, 1, 1)
        )
        ev6 = self.create_event(
            title='Past ended event',
            start_date=tz_datetime(2013, 1, 1),
            end_date=tz_datetime(2013, 1, 2),
            publish_at=tz_datetime(2013, 1, 1)
        )
        self.create_event(
            title='Other config, start in, end is Null',
            start_date=tz_datetime(2015, 2, 18),
            publish_at=tz_datetime(2015, 2, 10),
            app_config=other_config
        )

        events_list = [ev0, ev1, ev2, ev3, ev4, ev5, ev6]

        kwargs1 = {'year': '2014'}
        kwargs2 = {'year': '2015'}
        kwargs3 = {'year': '2016'}

        view_name = '{0}:events_list-by-year'.format(self.app_config.namespace)
        with force_language('en'):
            events_urls = [event.get_absolute_url() for event in events_list]
            view_url_2014 = reverse(view_name, kwargs=kwargs1)
            view_url_2015 = reverse(view_name, kwargs=kwargs2)
            view_url_2016 = reverse(view_name, kwargs=kwargs3)

        response1 = self.client.get(view_url_2014)
        # should contain all 2014 events
        self.response_contains(
            response1, [2, 3], events_list, events_urls)

        # ensure future events and past are not present
        self.response_not_contains(
            response1, [0, 1, 4, 5, 6], events_list, events_urls)

        response2 = self.client.get(view_url_2015)
        # should contain all 2015 events
        self.response_contains(
            response2, [0, 1, 2, 5], events_list, events_urls)
        # ensure past and future event is not present
        self.response_not_contains(
            response2, [3, 4, 6], events_list, events_urls)

        response3 = self.client.get(view_url_2016)
        # should contain events valid for 2016
        self.response_contains(
            response3, [1, 4], events_list, events_urls)

        # ensure past events are not present
        self.response_not_contains(
            response3, [0, 3, 2, 5, 6], events_list, events_urls)
