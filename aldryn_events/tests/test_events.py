# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple
import six

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from cms.utils.i18n import force_language
from parler.tests.utils import override_parler_settings
from parler.utils.conf import add_default_language_settings

from .base import EventBaseTestCase, tz_datetime
from ..models import Event

DateKey = namedtuple('DateKey', 'key_name, should_pass')


class EventTestCase(EventBaseTestCase):
    dates = {
        # same dates, force user to enter start time and end time,
        # OR change end date to something different
        DateKey('today-today', False): {
            'start_date': '2015-01-01',
            'end_date': '2015-01-01',
        },
        # end before start
        DateKey('today-yesterday', False): {
            'start_date': '2015-01-02',
            'end_date': '2015-01-01',
        },
        # ok, end in future
        DateKey('today-tomorrow', True): {
            'start_date': '2015-01-01',
            'end_date': '2015-01-02',
        },
        # same date and time
        DateKey('today-today-morning-morning', False): {
            'start_date': '2015-01-01',
            'end_date': '2015-01-01',
            'start_time': '10:00:00',
            'end_time': '10:00:00',
        },
        DateKey('today-today-morning-noon', True): {
            'start_date': '2015-01-01',
            'end_date': '2015-01-01',
            'start_time': '10:00:00',
            'end_time': '12:00:00',
        },
        # end time before start time
        DateKey('today-today-noon-morning', False): {
            'start_date': '2015-01-01',
            'end_date': '2015-01-01',
            'start_time': '12:00:00',
            'end_time': '10:00:00',
        },
        # no end date, only time
        # FIXME: Should we autofill end date to same as start?
        DateKey('today-none-noon-morning', True): {
            'start_date': '2015-01-01',
            'start_time': '12:00:00',
            'end_time': '10:00:00',
        },
        DateKey('today-none-noon-none', True): {
            'start_date': '2015-01-01',
            'start_time': '12:00:00',
        },
    }

    def test_event_days_property_shows_correct_value(self):
        event = Event(
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 1, 5)
        )
        self.assertEqual(event.days, 5)
        event.end_date = None
        self.assertEqual(event.days, 1)

    def test_no_start_date_raises_is_not_possible(self):
        with self.assertRaises(IntegrityError):
            Event.objects.create(
                title='5 days event', app_config=self.app_config,
            )

    def test_clean_with_allowed_dates_do_not_fail(self):
        failures = []
        for key, dates in self.dates.items():
            if not key.should_pass:
                continue
            event_data = self.make_default_values_with_new_dates(dates)
            event = Event(**event_data)
            try:
                event.clean()
            except Exception as e:
                failures.append((key, e))

        # if there were failures - raise explicitly with correct message
        if failures:
            msg = ("Event clean method failed when it shouldn't "
                   "for following keys: {0}")
            errors = '; '.join(
                ['key {0}, exception{1}'.format(str(key), str(ex))
                 for key, ex in failures])

            self.assertTrue(False, msg=msg.format(errors))

    def test_clean_with_not_allowed_dates_raises_validation_error(self):
        failures = []
        for key, dates in self.dates.items():
            if key.should_pass:
                continue
            event_data = self.make_default_values_with_new_dates(dates)
            event = Event(**event_data)

            # try to clean event, should rise validation error
            try:
                event.clean()
            except ValidationError as e:
                self.assertEqual(e.__class__, ValidationError)
            else:
                # instead of raising as soon as we hit error continue to run
                # till the end and memorize data which has been failed.
                failures.append(key)

        # if there were failures - raise explicitly with correct message
        if failures:
            msg = 'Failed to raise Validation error for following keys: {0}'
            errors = ('; '.join([str(key) for key in failures])
                      if len(failures) > 1 else str(failures[0]))
            self.assertTrue(False, msg=msg.format(errors))

    def test_event_creation_with_wrong_dates_format_raises_validationerror(
            self):
        with self.assertRaises(ValidationError):
            Event.objects.create(
                title='5 days event', app_config=self.app_config,
                start_date='blah'
            )
        with self.assertRaises(ValidationError):
            Event.objects.create(
                title='5 days event', app_config=self.app_config,
                start_date='2015-01-01', end_date='blah'
            )
        with self.assertRaises(ValidationError):
            Event.objects.create(
                title='5 days event', app_config=self.app_config,
                start_date='2015-01-01', end_date='2015-01-01',
                publish_at='blah'
            )

    def test_event_days_property_raises_validation_error(self):
        event = self.create_event(
            title='5 days event',
            start_date='2015-01-01'
        )
        event.start_date, event.end_date = 'blah', 'blah'
        self.assertRaises(ValidationError, lambda: event.days)
        event.start_date = '2015-01-01'
        self.assertRaises(ValidationError, lambda: event.days)

    def test_event_take_single_day_property(self):
        event1 = self.create_event(
            title='blah', start_date=tz_datetime(2015, 1, 1)
        )
        event2 = self.create_event(
            title='bleh',
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 1, 5)
        )
        self.assertTrue(event1.takes_single_day)
        self.assertFalse(event2.takes_single_day)

    def test_create_event(self):
        """
        We can create an event with a name in two languages
        """
        with force_language('en'):
            event = Event.objects.create(
                title='Concert', slug='open-concert',
                start_date=tz_datetime(2014, 9, 10),
                publish_at=tz_datetime(2014, 9, 9),
                app_config=self.app_config
            )
        self.assertEqual(Event.objects.translated('en').count(), 1)
        self.assertEqual(Event.objects.translated('de').count(), 0)

        event.create_translation('de', title='Konzert', slug='offene-konzert')

        self.assertEqual(Event.objects.translated('en').count(), 1)
        self.assertEqual(Event.objects.translated('de').count(), 1)

    def test_specific_language_characters_in_title(self):

        test_title = u"Sprachgefühl"
        with force_language('de'):
            event = Event.objects.create(
                title=test_title, slug='sprachgefuhl',
                start_date=tz_datetime(2014, 9, 10),
                publish_at=tz_datetime(2014, 9, 9),
                app_config=self.app_config
            )
        self.assertEqual(Event.objects.translated('de').count(), 1)
        self.assertEqual(test_title, event.title)
        self.assertIn(test_title, six.text_type(event))

    def test_behaviour_of_active_translations_and_hide_untranslated(self):
        self.create_event(title='test event', start_date='2015-01-01')

        self.assertEqual(Event.objects.active_translations('en').count(), 1)
        self.assertEqual(Event.objects.active_translations('de').count(), 1)
        self.assertEqual(Event.objects.active_translations('jp').count(), 1)

        parler_languages = add_default_language_settings({
            1: (
                {'code': 'en'},
                {'code': 'de'},
            ),
            'default': {
                'fallback': 'en',
                'hide_untranslated': True,
            }
        })

        with override_parler_settings(PARLER_LANGUAGES=parler_languages):
            self.assertEqual(
                Event.objects.active_translations('en').count(), 1
            )
            self.assertEqual(
                Event.objects.active_translations('de').count(), 0
            )
            self.assertEqual(
                Event.objects.active_translations('jp').count(), 0
            )

    def test_event_fill_slug_with_manager_create(self):
        event = Event.objects.create(
            title='show me the slug',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        self.assertEqual(event.slug, 'show-me-the-slug')

    def test_event_fill_slug_with_instance_save(self):
        event = Event(
            title='show me the slug',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        event.save()
        self.assertEqual(event.slug, 'show-me-the-slug')

    def test_event_not_overwrite_slug_with_manager_create(self):
        event = Event.objects.create(
            title='show me the slug',
            slug='gotchaa',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        self.assertEqual(event.slug, 'gotchaa')

    def test_event_not_overwrite_slug_with_instance_save(self):
        event = Event(
            title='show me the slug', slug='gotchaa',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        event.save()
        self.assertEqual(event.slug, 'gotchaa')
