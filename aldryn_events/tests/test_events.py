# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from cms.utils.i18n import force_language
from aldryn_events.models import Event
from .base import EventBaseTestCase, tz_datetime


class EventTestCase(EventBaseTestCase):

    def test_event_days_property_shows_correct_value(self):
        event = Event(
            start_date=tz_datetime(2015, 1, 1),
            end_date=tz_datetime(2015, 1, 5)
        )
        self.assertEqual(event.days, 5)
        event.end_date = None
        self.assertEqual(event.days, 1)

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
