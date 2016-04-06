# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import override
from aldryn_events.models import Event
from cms import api

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


class TestEventsManager(EventManagerTestCase):

    def test_ongoing(self):
        now = tz_datetime(2014, 4, 7, 9, 30)
        entries = [event.pk for event in
                   Event.objects.ongoing(now).order_by('pk')]
        # events with start date < now and end > now or is null
        expected = [event.pk for event in
                    [self.ev1, self.ev2, self.ev3, self.ev7]]
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


class EventManagerAppConfigTestCase(EventBaseTestCase):
    """
    Please add this TO THE LEFT of EventManagerTestCase if used with it.
    """
    def setUp(self):
        super(EventManagerAppConfigTestCase, self).setUp()
        # Ensure that all test events are assigned to an app_config
        self.events = [self.ev1, self.ev2, self.ev3, self.ev4, self.ev5,
                       self.ev6, self.ev7]
        for event in self.events:
            event.app_config = self.app_config

        self.root_page = self.create_root_page()
        self.page = api.create_page(
            'Events en', self.template, 'en', published=True,
            parent=self.root_page,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 8)
        )
        api.create_title('de', 'Events de', self.page)
        self.page.publish('en')
        self.page.publish('de')
        self.page.reload()
        # aldryn apphook reload needs a page load to work
        with override('en'):
            page_url = self.page.get_absolute_url()
        self.client.get(page_url)


class TestEventsAppConfigManager(EventManagerAppConfigTestCase,
                                 EventManagerTestCase):

    def setUp(self):
        super(TestEventsAppConfigManager, self).setUp()
        self.oldest_first = [self.ev1, self.ev7, self.ev2,
                             self.ev3, self.ev4, self.ev5]

    def test_normal_ordering(self):
        """
        Ensure that events are ordered oldest-first, which is the default
        for app-configs.
        """
        page_url = self.page.get_absolute_url()
        content = self.client.get(page_url).content.decode('utf-8')
        # NOTE: This list should be ordered in the events natural order
        for e in range(0, len(self.oldest_first) - 1):
            self.assertLess(content.find(self.oldest_first[e].title),
                            content.find(self.oldest_first[e + 1].title))

    def test_latest_first_ordering(self):
        """
        Ensure that events are ordered latest-first when app is configured
        to do so.
        """
        page_url = self.page.get_absolute_url()
        content = self.client.get(page_url).content.decode('utf-8')
        latest_first = reversed(self.oldest_first)
        self.app_config.latest_first = True
        # NOTE: This list should be ordered in the events natural order
        for e in range(0, len([latest_first]) - 1):
            self.assertLess(content.find(latest_first[e].title),
                            content.find(latest_first[e + 1].title))
