# -*- coding: utf-8 -*-

from django.test import TransactionTestCase
from aldryn_events.models import Event, EventsConfig
from aldryn_events.tests.base import EventBaseTestCase
from aldryn_events.utils import build_calendar
from datetime import date


class UtilsTestCase(EventBaseTestCase):

    def setUp(self):
        super(UtilsTestCase, self).setUp()
        self.config, created = (
            EventsConfig.objects.get_or_create(namespace='aldryn_events')
        )

    def test_build_calendar(self):
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event(
            title='ev1', start_date='2015-02-13', publish_at='2015-02-10'
        )
        ev2 = self.create_event(
            title='ev2', start_date='2015-02-15', publish_at='2015-02-10'
        )
        ev3 = self.create_event(
            de=dict(
                title='ev3', start_date='2015-02-16', publish_at='2015-02-10'
            )
        )
        ev4 = self.create_event(
            title='ev4', start_date='2015-02-18', publish_at='2015-02-10',
            app_config=other_config
        )
        ev5 = self.create_event(
            title='ev5', start_date='2015-02-22', end_date='2015-02-27',
            publish_at='2015-02-10'
        )
        ev6 = self.create_event(
            title='ev6', start_date='2015-02-25', publish_at='2015-02-10'
        )

        dates = build_calendar('2015', '02', 'en', self.config.namespace)

        # ev1 and ev2 in his days
        self.assertEqual(dates[date(2015, 2, 13)], [ev1])
        self.assertEqual(dates[date(2015, 2, 15)], [ev2])
        # ev3 is in German, we search for English
        self.assertEqual(dates[date(2015, 2, 16)], [])
        # ev4 is in other namespace
        self.assertEqual(dates[date(2015, 2, 18)], [])
        # ev5 has 5 days duration (whoa!)
        self.assertEqual(dates[date(2015, 2, 22)], [ev5])
        self.assertEqual(dates[date(2015, 2, 23)], [ev5])
        self.assertEqual(dates[date(2015, 2, 24)], [ev5])
        # ev6 happens while ev5
        self.assertEqual(dates[date(2015, 2, 25)], [ev5, ev6])
        self.assertEqual(dates[date(2015, 2, 26)], [ev5])
        self.assertEqual(dates[date(2015, 2, 27)], [ev5])

