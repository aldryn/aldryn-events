# -*- coding: utf-8 -*-

from aldryn_events.models import Event

from .base import EventBaseTestCase, tz_datetime


class EventManagerTestCase(EventBaseTestCase):

    """ Tests EventManager and EventQuerySet """

    def setUp(self):
        super(EventManagerTestCase, self).setUp()
        # happens in Apr 5
        self.ev1 = self.create_event(
            title='ev1',
            start_date=tz_datetime(2014, 4, 5),
            publish_at=tz_datetime(2014, 4, 1)
        )
        # Apr 6 12:00 to Apr 7 9:00
        self.ev2 = self.create_event(
            title='ev2',
            start_date=tz_datetime(2014, 4, 6),
            end_date=tz_datetime(2014, 4, 7),
            start_time='12:00', end_time='09:00',
            publish_at=tz_datetime(2014, 4, 2)
        )
        # happens in Apr 7
        self.ev3 = self.create_event(
            title='ev3',
            start_date=tz_datetime(2014, 4, 7),
            publish_at=tz_datetime(2014, 4, 3)
        )
        # happens in Apr 8
        self.ev4 = self.create_event(
            title='ev4',
            start_date=tz_datetime(2014, 4, 8),
            publish_at=tz_datetime(2014, 4, 4)
        )
        # Apr 9 to Apr 15
        self.ev5 = self.create_event(
            title='ev5',
            start_date=tz_datetime(2014, 4, 9),
            end_date=tz_datetime(2014, 4, 15),
            publish_at=tz_datetime(2014, 4, 4)
        )
        # should happens in Apr 6 but is not published
        self.ev6 = self.create_event(
            title='ev6',
            start_date=tz_datetime(2014, 4, 6),
            publish_at=tz_datetime(2014, 4, 1),
            is_published=False
        )
        # happens in Apr 6
        self.ev7 = self.create_event(
            title='ev7',
            start_date=tz_datetime(2014, 4, 6),
            publish_at=tz_datetime(2014, 4, 1),
        )

    def test_ongoing(self):
        now = tz_datetime(2014, 4, 7, 9, 30)
        entries = [event.pk for event in Event.objects.ongoing(now)]
        expected = [event.pk for event in [self.ev2, self.ev3]]
        self.assertEqual(entries, expected)

    def test_published(self):
        now = tz_datetime(2014, 4, 1)
        entries = [event.pk for event in Event.objects.published(now)]
        expected = [event.pk for event in [self.ev1, self.ev7]]
        self.assertEqual(entries, expected)

    def test_future(self):
        now = tz_datetime(2014, 4, 7)
        entries = [event.pk for event in Event.objects.future(now)]
        expected = [event.pk for event in
                    [self.ev2, self.ev3, self.ev4, self.ev5]]
        self.assertEqual(entries, expected)

    def test_archive(self):
        now = tz_datetime(2014, 4, 7)
        entries = [event.pk for event in Event.objects.archive(now)]
        expected = [event.pk for event in [self.ev7, self.ev1]]
        self.assertEqual(entries, expected)

    def test_past(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects
        # the count=1 exclude ev1
        actual1 = [event.pk for event in entries.past(1, now)]
        expected1 = [self.ev7.pk]
        self.assertEqual(actual1, expected1)
        actual2 = [event.pk for event in entries.past(5, now)]
        expected2 = [event.pk for event in [self.ev7, self.ev1]]
        self.assertEqual(actual2, expected2)

    def test_upcoming(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects
        # the count=1 exclude ev1
        actual1 = [event.pk for event in entries.upcoming(1, now)]
        self.assertEqual(actual1, [self.ev2.pk])

        actual2 = [event.pk for event in entries.upcoming(5, now)]
        expected2 = [event.pk for event in
                     [self.ev2, self.ev3, self.ev4, self.ev5]]
        self.assertEqual(actual2, expected2)
