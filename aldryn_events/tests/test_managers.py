# -*- coding: utf-8 -*-
import mock
from django.utils.timezone import get_current_timezone

from datetime import datetime
from aldryn_events.models import Event

from .base import EventBaseTestCase


class EventManagerTestCase(EventBaseTestCase):
    """ Tests EventManager and EventQuerySet """

    def setUp(self):
        super(EventManagerTestCase, self).setUp()
        # happens in Apr 5
        self.create_event(
            title='ev1', start_date='2014-04-05', publish_at='2014-04-01'
        )
        # Apr 6 12:00 to Apr 7 09:00
        ev2 = self.create_event(
            title='ev2',
            start_date='2014-04-06', end_date='2014-04-07',
            start_time='12:00', end_time='09:00',
            publish_at='2014-04-02'
        )
        # happens in Apr 7
        ev3 = self.create_event(
            title='ev3', start_date='2014-04-07', publish_at='2014-04-03'
        )
        # happens in Apr 8
        ev4 = self.create_event(
            title='ev4', start_date='2014-04-08', publish_at='2014-04-04'
        )
        # Apr 9 to Apr 15
        self.create_event(
            title='ev5', start_date='2014-04-09', end_date='2014-04-15',
            publish_at='2014-04-04'
        )
        # should happens in Apr 6 but is not published
        self.create_event(
            title='ev6', start_date='2014-04-06', publish_at='2014-04-01',
            is_published=False
        )
        # happens in Apr 6
        self.create_event(
            title='ev7', start_date='2014-04-06', publish_at='2014-04-01',
        )

    def test_ongoing(self):
        now = datetime(2014, 4, 7, 9, 30, tzinfo=get_current_timezone())
        entries = Event.objects.ongoing(now)
        self.assertQuerysetEqual(entries, ['ev2', 'ev3'], transform=str)

    def test_published(self):
        now = datetime(2014, 4, 1, tzinfo=get_current_timezone())
        entries = Event.objects.published(now)
        self.assertQuerysetEqual(entries, ['ev1', 'ev7'], transform=str)

    def test_future(self):
        now = datetime(2014, 4, 7, tzinfo=get_current_timezone())
        entries = Event.objects.future(now)
        self.assertQuerysetEqual(
            entries, ['ev2', 'ev3', 'ev4', 'ev5'], transform=str
        )

    def test_archive(self):
        now = datetime(2014, 4, 7, tzinfo=get_current_timezone())
        entries = Event.objects.archive(now)
        self.assertQuerysetEqual(entries, ['ev7', 'ev1'], transform=str)

    def test_past(self):
        now = datetime(2014, 4, 7, tzinfo=get_current_timezone())
        entries = Event.objects
        # the count=1 exclude ev1
        self.assertQuerysetEqual(entries.past(1, now), ['ev7'], transform=str)
        self.assertQuerysetEqual(
            entries.past(5, now), ['ev7', 'ev1'], transform=str
        )

    def test_upcoming(self):
        now = datetime(2014, 4, 7, tzinfo=get_current_timezone())
        entries = Event.objects
        # the count=1 exclude ev1
        self.assertQuerysetEqual(
            entries.upcoming(1, now), ['ev2'], transform=str
        )
        self.assertQuerysetEqual(
            entries.upcoming(5, now), ['ev2', 'ev3', 'ev4', 'ev5'],
            transform=str
        )
