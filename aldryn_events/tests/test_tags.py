# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase, TransactionTestCase
from django.utils.timezone import get_current_timezone
import mock
from pyquery import PyQuery
from aldryn_events.models import Event, EventsConfig
from django.template import Template, Context

class TagsTestCase(TransactionTestCase):

    def setUp(self):
        super(TagsTestCase, self).setUp()
        self.config, created = (
            EventsConfig.objects.get_or_create(namespace='aldryn_events')
        )

    def create_event(self, lang, title, start_date, end_date=None, slug=None,
                     config=None):
        return Event.objects.language(lang).create(
            title=title,
            slug=slug,
            start_date=start_date,
            end_date=end_date,
            app_config=config or self.config,
            start_time='00:00',
            end_time='23:59'
        )

    @mock.patch('aldryn_events.templatetags.aldryn_events.now')
    def test_calendar_tag_rendering(self, now_mock):
        now_mock.return_value = (
            datetime(2015, 1, 10, 12, 0, tzinfo=get_current_timezone())
        )
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event('en', 'ev1', '2015-01-13')
        ev2 = self.create_event('en', 'ev2', '2015-01-15')
        ev3 = self.create_event('de', 'ev3', '2015-01-16')
        ev4 = self.create_event('en', 'ev4', '2015-01-18', config=other_config)
        ev5 = self.create_event('en', 'ev5', '2015-01-22', '2015-01-27')
        ev6 = self.create_event('en', 'ev6', '2015-01-25')

        t = Template(
            "{% load aldryn_events %}"
            "{% calendar 2015 1 'en' 'aldryn_events' %}"
        )
        html = t.render(Context({}))
        table = PyQuery(html)('table.table-calendar')
        links = table.find('td.events').find('a')

        # test if tag rendered important elements
        self.assertEqual('1', table.attr('data-month-numeric'), )
        self.assertEqual('2015', table.attr('data-year'))
        self.assertEqual('10', table.find('td.today').text())
        self.assertEqual(8, links.length)  # 13, 15, 22, 23, 24, 25, 26, 27
        self.assertEqual('/en/events/2015/1/13/', links[0].attrib['href'])
        self.assertEqual('/en/events/2015/1/15/', links[1].attrib['href'])
        self.assertEqual('/en/events/2015/1/22/', links[2].attrib['href'])
        self.assertEqual('/en/events/2015/1/23/', links[3].attrib['href'])
        self.assertEqual('/en/events/2015/1/24/', links[4].attrib['href'])
        self.assertEqual('/en/events/2015/1/25/', links[5].attrib['href'])
        self.assertEqual('/en/events/2015/1/26/', links[6].attrib['href'])
        self.assertEqual('/en/events/2015/1/27/', links[7].attrib['href'])


