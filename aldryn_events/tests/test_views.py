# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import override

from cms import api

from aldryn_events.models import Event

from .base import EventBaseTestCase, tz_datetime


class TestEventViews(EventBaseTestCase):

    def setUp(self):
        super(TestEventViews, self).setUp()
        root_page = self.create_root_page()
        page = api.create_page(
            'Events en', self.template, 'en', published=True, parent=root_page,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 8)
        )
        api.create_title('de', 'Events de', page, slug='eventsapp')
        page.publish('en')
        page.publish('de')
        page.reload()
        # aldryn apphook reload needs some time to reload test
        # server implementation so we will provide some time for him
        # otherwise test_event_detail_view is too quick, and fails.
        with override('en'):
            page_url = page.get_absolute_url()
        self.client.get(page_url)

    def test_event_list_view(self):
        url = reverse("{0}:events_list".format(self.app_config.namespace))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_event_detail_view(self):
        with override("en"):
            event = Event.objects.create(**{
                'title': 'MyEvent',
                'slug': 'my-event',
                'start_date': tz_datetime(2015, 6, 1),
                'end_date': tz_datetime(2015, 7, 1),
                'app_config': self.app_config,
                'is_published': True,
            })
        url = event.get_absolute_url(language="en")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
