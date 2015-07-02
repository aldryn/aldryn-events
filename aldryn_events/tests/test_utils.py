# -*- coding: utf-8 -*-
from datetime import date

from aldryn_events.models import EventsConfig
from aldryn_events.utils import build_calendar

from .base import EventBaseTestCase, tz_datetime

NUM_WEEKS_DISPLAYED = 6


class UtilsTestCase(EventBaseTestCase):

    def test_build_calendar(self):
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event(
            title='ev1',
            start_date=tz_datetime(2015, 2, 13),
            publish_at=tz_datetime(2015, 2, 10)
        )
        ev2 = self.create_event(
            title='ev2',
            start_date=tz_datetime(2015, 2, 15),
            publish_at=tz_datetime(2015, 2, 10)
        )
        self.create_event(
            de=dict(
                title='ev3',
                start_date=tz_datetime(2015, 2, 16),
                publish_at=tz_datetime(2015, 2, 10)
            )
        )
        self.create_event(
            title='ev4',
            start_date=tz_datetime(2015, 2, 18),
            publish_at=tz_datetime(2015, 2, 10),
            app_config=other_config
        )
        ev5 = self.create_event(
            title='ev5',
            start_date=tz_datetime(2015, 2, 22),
            end_date=tz_datetime(2015, 2, 27),
            publish_at=tz_datetime(2015, 2, 10)
        )
        ev6 = self.create_event(
            title='ev6',
            start_date=tz_datetime(2015, 2, 25),
            publish_at=tz_datetime(2015, 2, 10)
        )

        dates = build_calendar('2015', '02', 'en', self.app_config.namespace)

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


class EventTestCase(EventBaseTestCase):

    def test_build_calendar_always_returns_correct_amount_of_days(self):
        # test that build_calendar utility method always returns appropriate
        # amount of days which is NUM_WEEKS_DISPLAYED * 7 (days in week).
        # Test against leap year and a regular year
        failed = []
        date_str = '{0}-{1}'
        for year in (2012, 2015):
            for month in range(1, 13):
                prepared_dates = len(build_calendar(
                    year=year, month=month, language='en',
                    namespace=self.app_config.namespace))
                if prepared_dates != 7 * NUM_WEEKS_DISPLAYED:
                    failed.append(
                        (date_str.format(month, year), prepared_dates))
        if failed:
            msg = 'Failed to get correct amount of dates for: {0}'
            error_appears = '; '.join(
                ['{0} returned {1} days'.format(date, days)
                 for date, days in failed])
            self.assertTrue(False, msg.format(error_appears))
