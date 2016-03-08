# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock

from django.template import Template
from django.utils.translation import override

from pyquery import PyQuery
from sekizai.context import SekizaiContext

from aldryn_events.models import EventsConfig

from .base import EventBaseTestCase, tz_datetime, get_page_request


class TagsTestCase(EventBaseTestCase):

    def setUp(self):
        super(TagsTestCase, self).setUp()
        other_config = EventsConfig.objects.create(namespace='other')
        self.create_event(
            title='ev1',
            start_date=tz_datetime(2015, 1, 13),
            end_date=tz_datetime(2015, 1, 14),
            publish_at=tz_datetime(2015, 1, 10)
        )
        self.create_event(
            title='ev2',
            start_date=tz_datetime(2015, 1, 15),
            end_date=tz_datetime(2015, 1, 15),
            publish_at=tz_datetime(2015, 1, 10)
        )
        self.create_event(
            de=dict(
                title='ev3',
                start_date=tz_datetime(2015, 1, 16),
                end_date=tz_datetime(2015, 1, 17),
                publish_at=tz_datetime(2015, 1, 10)
            )
        )
        self.create_event(
            title='ev4',
            start_date=tz_datetime(2015, 1, 18),
            publish_at=tz_datetime(2015, 1, 10),
            app_config=other_config
        )
        self.create_event(
            title='ev5',
            start_date=tz_datetime(2015, 1, 22),
            end_date=tz_datetime(2015, 1, 27),
            publish_at=tz_datetime(2015, 1, 10)
        )
        self.create_event(
            title='ev6',
            start_date=tz_datetime(2015, 1, 25),
        )

    def get_template(self, namespace):
        template_str = """
        {%% load aldryn_events %%}
        {%% calendar 2015 1 namespace='%s' %%}
        """ % namespace
        template = Template(template_str)
        return template

    def get_context(self, page):
        request = get_page_request(page)
        context = {
            'request': request,
        }
        return context

    @mock.patch('aldryn_events.templatetags.aldryn_events.timezone')
    def test_calendar_tag_rendering_en_only(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2015, 1, 10, 12)
        page_with_apphook = self.create_base_pages(multilang=False)
        # make use of default tests self.app_config namespace, instead of
        # hard coding it
        t = self.get_template(self.app_config.namespace)
        context = self.get_context(page_with_apphook)
        with override('en'):
            html = t.render(SekizaiContext(context))
            table = PyQuery(html)('table.js-calendar-table')
            page_url_en = page_with_apphook.get_absolute_url()
        links = table.find('td.events, td.multiday-events').find('a')
        # test if tag rendered important elements
        self.assertEqual('1', table.attr('data-month-numeric'), )
        self.assertEqual('2015', table.attr('data-year'))
        self.assertEqual('10', table.find('td.today').text())
        expected_days = (13, 14, 15, 22, 23, 24, 25, 26, 27)
        for position, day in enumerate(expected_days):
            event_url = '{0}2015/1/{1}/'.format(page_url_en, day)
            rendered_url = links[position].attrib['href']
            self.assertEqual(event_url, rendered_url)

    @mock.patch('aldryn_events.templatetags.aldryn_events.timezone')
    def test_calendar_tag_rendering_en_and_de(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2015, 1, 10, 12)
        page_with_apphook = self.create_base_pages(multilang=True)
        # make use of default tests self.app_config namespace, instead of
        # hard coding it
        t = self.get_template(self.app_config.namespace)
        context = self.get_context(page_with_apphook)
        with override('en'):
            html = t.render(SekizaiContext(context))
            table = PyQuery(html)('table.js-calendar-table')
            page_with_apphook.get_absolute_url()
        links = table.find('td.events, td.multiday-events').find('a')
        # test if tag rendered important elements
        self.assertEqual('1', table.attr('data-month-numeric'), )
        self.assertEqual('2015', table.attr('data-year'))
        self.assertEqual('10', table.find('td.today').text())
        # should include DE only event as well
        expected_days = (13, 14, 15, 16, 17, 22, 23, 24, 25, 26, 27)
        for position, day in enumerate(expected_days):
            # page url may vary depending on fallback settings, check only
            # against the date.
            event_url = '/2015/1/{0}/'.format(day)
            rendered_url = links[position].attrib['href']
            self.assertGreater(rendered_url.find(event_url), -1)
