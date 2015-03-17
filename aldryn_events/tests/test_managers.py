# -*- coding: utf-8 -*-

from aldryn_events.models import Event

from .base import EventBaseTestCase, tz_datetime


class EventManagerTestCase(EventBaseTestCase):

    """ Tests EventManager and EventQuerySet """

    def setUp(self):
        super(EventManagerTestCase, self).setUp()
        # happens in Apr 5
        self.create_event(
            title='ev1',
            start_date=tz_datetime(2014, 4, 5),
            publish_at=tz_datetime(2014, 4, 1)
        )
        # Apr 6 12:00 to Apr 7 9:00
        self.create_event(
            title='ev2',
            start_date=tz_datetime(2014, 4, 6),
            end_date=tz_datetime(2014, 4, 7),
            start_time='12:00', end_time='09:00',
            publish_at=tz_datetime(2014, 4, 2)
        )
        # happens in Apr 7
        self.create_event(
            title='ev3',
            start_date=tz_datetime(2014, 4, 7),
            publish_at=tz_datetime(2014, 4, 3)
        )
        # happens in Apr 8
        self.create_event(
            title='ev4',
            start_date=tz_datetime(2014, 4, 8),
            publish_at=tz_datetime(2014, 4, 4)
        )
        # Apr 9 to Apr 15
        self.create_event(
            title='ev5',
            start_date=tz_datetime(2014, 4, 9),
            end_date=tz_datetime(2014, 4, 15),
            publish_at=tz_datetime(2014, 4, 4)
        )
        # should happens in Apr 6 but is not published
        self.create_event(
            title='ev6',
            start_date=tz_datetime(2014, 4, 6),
            publish_at=tz_datetime(2014, 4, 1),
            is_published=False
        )
        # happens in Apr 6
        self.create_event(
            title='ev7',
            start_date=tz_datetime(2014, 4, 6),
            publish_at=tz_datetime(2014, 4, 1),
        )

    def test_ongoing(self):
        now = tz_datetime(2014, 4, 7, 9, 30)
        entries = Event.objects.ongoing(now)
        self.assertQuerysetEqual(entries, ['ev2', 'ev3'], transform=str)

    def test_published(self):
        now = tz_datetime(2014, 4, 1)
        entries = Event.objects.published(now)
        self.assertQuerysetEqual(entries, ['ev1', 'ev7'], transform=str)

    def test_future(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects.future(now)
        self.assertQuerysetEqual(
            entries, ['ev2', 'ev3', 'ev4', 'ev5'], transform=str
        )

    def test_archive(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects.archive(now)
        self.assertQuerysetEqual(entries, ['ev7', 'ev1'], transform=str)

    def test_past(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects
        # the count=1 exclude ev1
        self.assertQuerysetEqual(entries.past(1, now), ['ev7'], transform=str)
        self.assertQuerysetEqual(
            entries.past(5, now), ['ev7', 'ev1'], transform=str
        )

    def test_upcoming(self):
        now = tz_datetime(2014, 4, 7)
        entries = Event.objects
        # the count=1 exclude ev1
        self.assertQuerysetEqual(
            entries.upcoming(1, now), ['ev2'], transform=str
        )
        self.assertQuerysetEqual(
            entries.upcoming(5, now), ['ev2', 'ev3', 'ev4', 'ev5'],
            transform=str
        )
