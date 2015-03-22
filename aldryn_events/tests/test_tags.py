# -*- coding: utf-8 -*-
import mock

from django.template import Template, Context

from pyquery import PyQuery
from sekizai.context import SekizaiContext

from aldryn_events.models import EventsConfig

from .base import EventBaseTestCase, tz_datetime


class TagsTestCase(EventBaseTestCase):

    @mock.patch('aldryn_events.templatetags.aldryn_events.timezone')
    def test_calendar_tag_rendering(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2015, 1, 10, 12)
        self.create_base_pages()
        other_config = EventsConfig.objects.create(namespace='other')
        self.create_event(
            title='ev1',
            start_date=tz_datetime(2015, 1, 13),
            publish_at=tz_datetime(2015, 1, 10)
        )
        self.create_event(
            title='ev2',
            start_date=tz_datetime(2015, 1, 15),
            publish_at=tz_datetime(2015, 1, 10)
        )
        self.create_event(
            de=dict(
                title='ev3',
                start_date=tz_datetime(2015, 1, 16),
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
        t = Template(
            "{% load aldryn_events %}"
            "{% calendar 2015 1 'en' 'aldryn_events' %}"
        )
        html = t.render(SekizaiContext({}))
        table = PyQuery(html)('table.table-calendar')
        links = table.find('td.events').find('a')

        # test if tag rendered important elements
        self.assertEqual('1', table.attr('data-month-numeric'), )
        self.assertEqual('2015', table.attr('data-year'))
        self.assertEqual('10', table.find('td.today').text())
        self.assertEqual(8, links.length)  # 13, 15, 22, 23, 24, 25, 26, 27
        self.assertEqual('/en/eventsapp/2015/1/13/', links[0].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/15/', links[1].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/22/', links[2].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/23/', links[3].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/24/', links[4].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/25/', links[5].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/26/', links[6].attrib['href'])
        self.assertEqual('/en/eventsapp/2015/1/27/', links[7].attrib['href'])
