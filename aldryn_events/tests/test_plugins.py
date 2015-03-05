# -*- coding: utf-8 -*-
from cms import api
from cms.utils.i18n import force_language
from django.core.urlresolvers import reverse
from django.template import RequestContext
import mock
from aldryn_events.models import Event
from aldryn_events.tests.base import (
    EventBaseTestCase, tz_datetime, get_page_request
)


def calendar_url(year, month, language):
    with force_language(language):
        url = reverse(
            'admin:get-calendar-dates', kwargs={'year': year, 'month': month}
        )
    return url


class EventPluginsTestCase(EventBaseTestCase):

    def new_event_from_num(self, num, start_date, end_date, publish_at):
        """ create event based on a num in both languages """
        text, text_de = 'event', 'ereignis'
        event = self.create_event(
            title='{0} {1} en'.format(text, num),
            slug='{0}-{1}-en'.format(text, num),
            start_date=start_date, end_date=end_date,
            publish_at=publish_at,
            de={
                'title': '{0} {1} de'.format(text_de, num),
                'slug': '{0}-{1}-de'.format(text_de, num)
            }
        )
        return Event.objects.language('en').get(pk=event.pk)

    @mock.patch('aldryn_events.managers.timezone')
    def test_event_list_plugin(self, timezone_mock):
        """
        We add an event to the Event Plugin and look it up
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2, 12),

        # default event start_date='2014-09-10' publish_at='2014-01-01 12:00'
        event1 = self.create_default_event()
        with force_language('en'):
            event2 = Event.objects.create(
                title='Event2014 only english',
                start_date=tz_datetime(2014, 1, 29),
                publish_at=tz_datetime(2014, 1, 1, 12),
                app_config=self.app_config
            )

        root_page = self.create_root_page()
        page = api.create_page(
            'Events en', self.template, 'en', published=True,
            parent=root_page,
        )
        api.create_title('de', 'Events de', page)
        ph = page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'EventListCMSPlugin', 'en', app_config=self.app_config,
        )
        plugin_de = api.add_plugin(
            ph, 'EventListCMSPlugin', 'de', app_config=self.app_config,
        )
        plugin_en.events = [event1, event2]
        plugin_en.save()
        plugin_de.events = [event1]
        plugin_de.save()
        page.publish('en')
        page.publish('de')

        # EN: test plugin rendering
        with force_language('en'):
            response = self.client.get('/en/events-en/')
            event1.set_current_language('en')
            self.assertContains(response, event1.title)
            self.assertContains(response, event1.get_absolute_url())
            event2.set_current_language('en')
            self.assertContains(response, event2.title)
            self.assertContains(response, event2.get_absolute_url())

        # DE: test plugin rendering
        with force_language('de'):
            response = self.client.get('/de/events-de/')
            event1.set_current_language('de')
            self.assertContains(response, event1.title)
            self.assertContains(response, event1.get_absolute_url())
            self.assertNotContains(response, event2.title)
            self.assertNotContains(response, event2.get_absolute_url())

    @mock.patch('aldryn_events.managers.timezone')
    def test_upcoming_plugin_for_future(self, timezone_mock):
        """
        Test the upcoming events plugin
        """

        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)

        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
        )
        api.create_title('de', 'Home de', page)
        ph = page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'UpcomingPlugin', 'en', app_config=self.app_config
        )
        plugin_de = api.add_plugin(
            ph, 'UpcomingPlugin', 'de', app_config=self.app_config
        )
        page.publish('en')
        page.publish('de')

        for i in range(1, 7):
            self.new_event_from_num(
                i,
                start_date=tz_datetime(2014, 1, 29),
                end_date=tz_datetime(2014, 2, 5),
                publish_at=tz_datetime(2014, 1, 1, 12)
            )

        # Test plugin rendering for both languages in a forloop. I don't
        # like it but save lot of text space since we test for 5 entries
        rendered = {}
        with force_language('en'):
            request = get_page_request(None, path='/en/home/', language='en')
            context = RequestContext(request, {})
            rendered['en'] = plugin_en.render_plugin(context, ph)
        with force_language('de'):
            request = get_page_request(None, path='/de/home/', language='de')
            context = RequestContext(request, {})
            rendered['de'] = plugin_de.render_plugin(context, ph)

        for i in range(1, 6):
            for lang in ['en', 'de']:
                text = 'event' if lang == 'en' else 'ereignis'
                name = '{0} {1} {2}'.format(text, i, lang)
                url = '/{2}/events/{0}-{1}-{2}/'.format(text, i, lang)
                self.assertIn(
                    name, rendered[lang],
                    'Title "{0}" not found in rendered plugin for '
                    'language "{1}".'.format(name, lang)
                )
                self.assertIn(
                    url, rendered[lang],
                    'URL "{0}" not found in rendered plugin for '
                    'language "{1}".'.format(url, lang)
                )

        self.assertNotIn(
            'event 6 en', rendered,
            'Title "event 6 en" found in rendered plugin, but limit is '
            '5 entries.'
        )
        self.assertNotIn(
            'event-6-en', rendered,
            'URL "event-6-en" found in rendered plugin, but limit is '
            '5 entries.'
        )
        self.assertNotIn(
            'event 6 de', rendered,
            'Title "event 6 de" found in rendered plugin, but limit '
            'is 5 entries.'
        )
        self.assertNotIn(
            'event-6-de', rendered,
            'URL "event-6-de" found in rendered plugin, but limit '
            'is 5 entries.'

        )

    @mock.patch('aldryn_events.managers.timezone')
    def test_upcoming_plugin_for_past(self, timezone_mock):
        """
        Test the upcoming events plugin for past entries
        """
        timezone_mock.now.return_value = tz_datetime(2014, 7, 6, 12)
        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace
        )
        api.create_title('de', 'Home de', page)
        ph = page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(ph, 'UpcomingPlugin', 'en',
                                   app_config=self.app_config)
        plugin_de = api.add_plugin(ph, 'UpcomingPlugin', 'de',
                                   app_config=self.app_config)
        plugin_en.past_events, plugin_de.past_events = True, True
        plugin_en.save()
        plugin_de.save()
        page.publish('en')
        page.publish('de')

        for i in range(1, 7):
            self.new_event_from_num(
                i,
                start_date=tz_datetime(2014, 6, 29),
                end_date=tz_datetime(2014, 7, 5),
                publish_at=tz_datetime(2014, 6, 20, 12)
            )

        # Test plugin rendering for both languages in a forloop. I don't
        # like it but save lot of text space since we test for 5 entries
        rendered = {}
        with force_language('en'):
            request = get_page_request(None, path='/en/home/', language='en')
            context = RequestContext(request, {})
            rendered['en'] = plugin_en.render_plugin(context, ph)
        with force_language('de'):
            request = get_page_request(None, path='/de/home/', language='de')
            context = RequestContext(request, {})
            rendered['de'] = plugin_de.render_plugin(context, ph)

        for i in range(1, 6):
            for lang in ['en', 'de']:
                text = 'event' if lang == 'en' else 'ereignis'
                name = '{0} {1} {2}'.format(text, i, lang)
                url = '/{2}/events/{0}-{1}-{2}/'.format(text, i, lang)
                self.assertIn(
                    name, rendered[lang],
                    'Title "{0}" not found in rendered plugin for '
                    'language "{1}".'.format(name, lang)
                )
                self.assertIn(
                    url, rendered[lang],
                    'URL "{0}" not found in rendered plugin for '
                    'language "{1}".'.format(url, lang)
                )

        self.assertNotIn(
            'event 6 en', rendered,
            'Title "event 6 en" found in rendered plugin, but limit is 5 '
            'entries.'
        )
        self.assertNotIn(
            'event-6-en', rendered,
            'URL "event-6-en" found in rendered plugin, but limit is 5 '
            'entries.'
        )
        self.assertNotIn(
            'event 6 de', rendered,
            'Title "event 6 de" found in rendered plugin, but limit is 5 '
            'entries.'
        )
        self.assertNotIn(
            'event-6-de', rendered,
            'URL "event-6-de" found in rendered plugin, but limit is 5 '
            'entries.'
        )

    @mock.patch('aldryn_events.managers.timezone')
    @mock.patch('aldryn_events.cms_plugins.timezone')
    def test_calendar_plugin(self, timezone_mock, plugin_timezone_mock):
        """
        This plugin should show a link to event list page on days that has
        events
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        plugin_timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
            publication_date=tz_datetime(2014, 1, 2)
        )

        api.create_title('de', 'Home de', page)
        ph = page.placeholders.get(slot='content')
        plugins = {
            'en': api.add_plugin(
                ph, 'CalendarPlugin', 'en', app_config=self.app_config
            ),
            'de': api.add_plugin(
                ph, 'CalendarPlugin', 'de', app_config=self.app_config
            )
        }
        page.publish('en')
        page.publish('de')

        for i in range(1, 7):
            self.new_event_from_num(
                i,
                start_date=tz_datetime(2014, 1, 29, 12),
                end_date=tz_datetime(2014, 2, 5, 12),
                publish_at=tz_datetime(2014, 1, 1, 12)
            )

        # add a event for next month to check if date is rendered
        self.new_event_from_num(
            7,
            start_date=tz_datetime(2014, 2, 10, 12),
            end_date=tz_datetime(2014, 2, 15, 1),
            publish_at=tz_datetime(2014, 1, 1, 12)
        )
        rendered = {}

        with force_language('en'):
            rendered['en'] = {
                'p1': self.client.get(page.get_absolute_url()).content,
                'p2': self.client.get(
                    "{0}?plugin_pk={1}".format(
                        calendar_url(2014, 2, 'en'), plugins['en'].pk
                    )
                ).content
            }
        with force_language('de'):
            rendered['de'] = {
                'p1': self.client.get(page.get_absolute_url()).content,
                'p2': self.client.get(
                    "{0}?plugin_pk={1}".format(
                        calendar_url(2014, 2, 'de'), plugins['de'].pk
                    )
                ).content
            }

        html_p1 = ('<td class="events"><a href="/{0}/events/2014/1/29/">'
                   '29</a></td>')
        html_p2 = ('<td class="events"><a href="/{0}/events/2014/2/10/">'
                   '10</a></td>')
        self.assertIn(
            html_p1.format('de'), rendered['de']['p1'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html_p1.format('de'), 'DE')
        )
        self.assertIn(
            html_p1.format('en'), rendered['en']['p1'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html_p1.format('en'), 'EN')
        )

        self.assertIn(
            html_p2.format('de'), rendered['de']['p2'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html_p2.format('de'), 'DE')
        )
        self.assertIn(
            html_p2.format('en'), rendered['en']['p2'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html_p2.format('en'), 'EN')
        )
