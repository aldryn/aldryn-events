# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase, TransactionTestCase
from django.utils.timezone import get_current_timezone
import mock
from pyquery import PyQuery
from aldryn_events.models import Event, EventsConfig
from django.template import Template, Context
from aldryn_events.tests.base import EventBaseTestCase


class TagsTestCase(EventBaseTestCase):

    @mock.patch('aldryn_events.templatetags.aldryn_events.timezone')
    def test_calendar_tag_rendering(self, timezone_mock):
        timezone_mock.now.return_value = (
            datetime(2015, 1, 10, 12, 0, tzinfo=get_current_timezone())
        )
        other_config = EventsConfig.objects.create(namespace='other')
        ev1 = self.create_event(
            title='ev1', start_date='2015-01-13', publish_at='2015-01-10'
        )
        ev2 = self.create_event(
            title='ev2', start_date='2015-01-15', publish_at='2015-01-10'
        )
        ev3 = self.create_event(
            de=dict(
                title='ev3', start_date='2015-01-16', publish_at='2015-01-10'
            )
        )
        ev4 = self.create_event(
            title='ev4', start_date='2015-01-18', publish_at='2015-01-10',
            app_config=other_config
        )
        ev5 = self.create_event(
            title='ev5', start_date='2015-01-22', end_date='2015-01-27',
            publish_at='2015-01-10'
        )
        ev6 = self.create_event(
            title='ev6', start_date='2015-01-25', publish_at='2015-01-10'
        )

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


