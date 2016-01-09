# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import attrgetter

import datetime
from django.utils import timezone

from aldryn_events.models import EventsConfig
from aldryn_events.utils import build_calendar

from .base import EventBaseTestCase, tz_datetime

NUM_WEEKS_DISPLAYED = 6


class UtilsTestCase(EventBaseTestCase):

    def test_build_calendar(self):
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event(
            title='Start in, end in',
            start_date=tz_datetime(2015, 2, 1),
            end_date=tz_datetime(2015, 2, 10),
            publish_at=tz_datetime(2015, 2, 1)
        )
        ev2 = self.create_event(
            title='Start in, end greater',
            start_date=tz_datetime(2015, 2, 15),
            end_date=tz_datetime(2015, 4, 27),
            publish_at=tz_datetime(2015, 2, 10)
        )

        ev3 = self.create_event(
            title='Start less, end in',
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 2, 15),
            publish_at=tz_datetime(2015, 1, 1)
        )
        self.create_event(
            title='Start less, end is Null',
            start_date=tz_datetime(2015, 1, 1),
            publish_at=tz_datetime(2015, 1, 1)
        )

        self.create_event(
            de=dict(
                title='German, start in, end in',
                start_date=tz_datetime(2015, 2, 16),
                publish_at=tz_datetime(2015, 2, 10)
            )
        )
        self.create_event(
            title='Other config, start in, end is Null',
            start_date=tz_datetime(2015, 2, 18),
            publish_at=tz_datetime(2015, 2, 10),
            app_config=other_config
        )

        dates = build_calendar('2015', '02', 'en', self.app_config.namespace)

        def sorted_events_for_date(*args):
            """
            Returns sorted events for provided date (args tuple).
            :param args: (year, month, day)
            :return: sorted list of events for provided date
            """
            date = datetime.date(*args)
            return sorted(dates[date], key=attrgetter('pk'))
        # (start less, end in) and (start in, end in)
        # + out of calendar events (active)
        self.assertEqual(sorted_events_for_date(2015, 2, 1), [ev1, ev3])
        # (start in, end greater) and (start less, end in)
        # + out of calendar events (active)
        self.assertEqual(sorted_events_for_date(2015, 2, 15), [ev2, ev3])
        # Should not contain DE event, but this date includes ev2
        # + out of calendar events (active)
        self.assertEqual(sorted_events_for_date(2015, 2, 16), [ev2])
        # Should not contain events from other namespace, but should contain
        # out of calendar events (active)
        self.assertEqual(sorted_events_for_date(2015, 2, 18), [ev2])

    def test_build_calendar_ongoing_event_ends_this_month(self):
        # tests that event that was started outside of calendar tag scope
        # and ends in calendar scope is present in the output
        now = timezone.now()
        start = now - datetime.timedelta(days=60)
        end = now

        event = self.create_event(
            title='Long term event',
            start_date=start,
            end_date=end,
            publish_at=start
        )
        output = build_calendar(
            now.year,
            now.month,
            'en',
            self.app_config.namespace)
        day_before = now - datetime.timedelta(days=1)
        self.assertIn(event, output[day_before.date()])

    def test_build_calendar_ongoing_event_ends_out_of_calendar(self):
        # tests that event that was started outside of calendar tag scope
        # and ends outside the scope is present in the output
        now = timezone.now()
        start = now - datetime.timedelta(days=60)
        end = now + datetime.timedelta(days=60)

        event = self.create_event(
            title='Long term event',
            start_date=start,
            end_date=end,
            publish_at=start
        )
        output = build_calendar(
            now.year,
            now.month,
            'en',
            self.app_config.namespace)
        day_before = now - datetime.timedelta(days=1)
        self.assertIn(event, output[day_before.date()])

    def test_build_calendar_ongoing_event_starts_ends_out_of_calendar(self):
        # tests that event that was started and ends outside of calendar
        # tag scope is present in the output
        now = timezone.now()
        start = now - datetime.timedelta(days=180)
        end = now + datetime.timedelta(days=180)

        event = self.create_event(
            title='Long term event',
            start_date=start,
            end_date=end,
            publish_at=start
        )
        output = build_calendar(
            now.year,
            now.month,
            'en',
            self.app_config.namespace)
        day_before = now - datetime.timedelta(days=1)
        self.assertIn(event, output[day_before.date()])

    def test_build_calendar_ongoing_event_starts_out_of_calendar_no_end(self):
        # tests that event that was started and without end date is
        # not present in the output
        now = timezone.now()
        start = now - datetime.timedelta(days=180)

        event = self.create_event(
            title='Long term event',
            start_date=start,
            publish_at=start
        )
        output = build_calendar(
            now.year,
            now.month,
            'en',
            self.app_config.namespace)
        day_before = now - datetime.timedelta(days=1)
        self.assertNotIn(event, output[day_before.date()])


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
