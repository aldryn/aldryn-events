# -*- coding: utf-8 -*-

from django.test import TestCase
from aldryn_events.models import Event, EventsConfig
from aldryn_events.utils import build_calendar
from datetime import date


class UtilsTestCase(TestCase):

    def setUp(self):
        self.config = EventsConfig.objects.create(namespace='aldryn_events')

    def create_event(self, lang, title, start_date, end_date=None, slug=None,
                     config=None):
        return Event.objects.language(lang).create(
            title=title,
            slug=slug,
            start_date=start_date,
            end_date=end_date,
            app_config=config or self.config,
            start_time='00:00',
            end_time='23:59'
        )

    def test_build_calendar(self):
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event('en', 'ev1', '2015-02-13')
        ev2 = self.create_event('en', 'ev2', '2015-02-15')
        ev3 = self.create_event('de', 'ev3', '2015-02-16')
        ev4 = self.create_event('en', 'ev4', '2015-02-18', config=other_config)
        ev5 = self.create_event('en', 'ev5', '2015-02-22', '2015-02-27')
        ev6 = self.create_event('en', 'ev6', '2015-02-25')

        # make dates a dict cuz is easy to test
        dates = dict(build_calendar('2015', '02', 'en', self.config.namespace))

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

