# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from cms import api
from cms.models import Placeholder
from cms.utils.i18n import force_language
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.cache import cache
from django.utils.encoding import force_text

import mock
from aldryn_events.models import Event, EventsConfig
from aldryn_events.tests.base import (
    EventBaseTestCase, tz_datetime
)
from aldryn_events.utils import is_valid_namespace


def calendar_url(year, month, language, namespace):
    with force_language(language):
        url = reverse(
            '{0}:get-calendar-dates'.format(namespace),
            kwargs={'year': year, 'month': month}
        )
    return url


class TestPluginLanguageHelperMixin(object):

    def create_obj_with_translation(self, **kwargs):
        data = dict(
            title='Event Foo',
            slug='event-foo',
            start_date=tz_datetime(2014, 1, 1),
            publish_at=tz_datetime(2000, 1, 1),
            de={'title': 'Event Foo DE', 'slug': 'event-foo-de'}
        )
        data.update(kwargs)
        return self.create_event(**data)

    def _test_plugin_languages(self, plugin_type, populate_func):
        """Test plugins for rendering objects in unpublished app language"""
        app_page = self.create_base_pages(multilang=True)
        # 'en' is the default language for our tests
        language_code = 'en'
        plugin_page = api.create_page(
            'Events plugins page {0}'.format(language_code), self.template,
            language_code, parent=self.root_page,
        )
        ph = plugin_page.placeholders.get(slot='content')
        plugin = api.add_plugin(
            ph, plugin_type, language_code, app_config=self.app_config,
        )
        populate_func(plugin)
        plugin_page.publish(language_code)

        # Unpublish page with the apphook
        app_page.unpublish(language_code)
        cache.clear()

        try:
            with force_language(language_code):
                response = self.client.get(plugin_page.get_absolute_url())
                # check we've received non-empty response
                self.assertTrue(response.status_code, 200)
        except NoReverseMatch:
            self.fail("NoReverseMatch was raised during plugin page rendering")


class EventConfigPlaceholdersTestCase(EventBaseTestCase):

    def setUp(self):
        super(EventConfigPlaceholdersTestCase, self).setUp()
        self.page_with_apphook = self.create_base_pages()

    def test_event_config_placeholders_are_usable(self):
        # make sure default config is apphooked to a page.
        # FIXME: until migrations are not enabled and ensured to work with
        # tests - this wont test the default adryn_events namespace =(
        # though this test is (or at least it should be) pretty useful.
        default_events_config = EventsConfig.objects.get_or_create(
            namespace='aldryn_events')[0]
        if not is_valid_namespace(default_events_config.namespace):
            page = api.create_page(
                title='default events config en', template=self.template,
                language='en',
                published=True,
                parent=self.root_page,
                apphook='EventListAppHook',
                apphook_namespace=default_events_config.namespace,
                publication_date=tz_datetime(2014, 6, 8)
            )
            api.create_title('de', 'default events config en', page)
            page.publish('en')
            page.publish('de')
            page_with_default_config = page.reload()
            # get some time for aldryn-apphook-reload to perform actions
            with force_language('en'):
                default_config_url = page_with_default_config.get_abolute_url()
            self.client.get(default_config_url)

        configs = EventsConfig.objects.all()
        # this would be used to build unique value for text plugin
        # namespace-lang-placeholder_name, which would be searched on the page.
        plugin_content_raw = '{0}-{1}-{2}'
        plugins_content = {}
        for cfg in configs:
            cfg_placehodlers = [field for field in cfg._meta.fields
                                if field.__class__ == Placeholder]
            placeholders_names = [placeholder.name for placeholder in
                                  cfg_placehodlers]
            # make sure that we have an empty list to store plugins content
            plugins_content[cfg] = []
            for placeholder_name in placeholders_names:
                placeholder_instance = getattr(cfg, placeholder_name, None)
                self.assertNotEqual(type(placeholder_instance), type(None))
                plugin_text = plugin_content_raw.format(
                    cfg.namespace, 'en', placeholder_name)
                api.add_plugin(
                    placeholder_instance, 'TextPlugin', 'en',
                    body=plugin_text)
                # track other namespaces plugin content to check
                # their uniqueness
                plugins_content[cfg].append(plugin_text)

        # test EventsConfig placeholder content if it is attached to a page
        skipped = []
        for cfg in configs:
            if not is_valid_namespace(cfg.namespace):
                skipped.append(cfg)
                continue

            with force_language('en'):
                apphook_url = reverse('{0}:events_list'.format(cfg.namespace))
            response = self.client.get(apphook_url)

            # test own content
            for text in plugins_content[cfg]:
                self.assertIn(response, text)

            # make sure other namespace plugins are not leaked
            other_configs = [config for config in plugins_content.keys()
                             if config is not cfg]
            all_other_namespace_plugins_text = [
                text for other_config in other_configs
                for text in plugins_content[other_config]]
            for other_plugins_text in all_other_namespace_plugins_text:
                self.assertNotIn(response, other_plugins_text)
        # make sure that we tested at least one config
        self.assertNotEqual(configs.count(), len(skipped))


class EventPluginsTestCase(TestPluginLanguageHelperMixin, EventBaseTestCase):

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
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2, 12)
        # default event start_date='2014-09-10' publish_at='2014-01-01 12:00'
        event1 = self.create_event(
            title='Event2014',
            slug='open-air',
            start_date=tz_datetime(2014, 9, 10),
            publish_at=tz_datetime(2014, 1, 1, 9),
            de={'title': 'Ereignis', 'slug': 'im-freien'}
        )
        event2 = self.create_event(
            title='Event2014 only english',
            start_date=tz_datetime(2014, 1, 29),
            publish_at=tz_datetime(2014, 1, 1, 12)
        )

        root_page = self.create_root_page()
        page = api.create_page(
            'Events en', self.template, 'en', published=True, parent=root_page,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 8)
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
            self.assertContains(response, event2.title)
            self.assertContains(response, event2.get_absolute_url())

    def test_event_list_plugin_languages(self):
        def populate_event_list_plugin(plugin):
            plugin.events = [self.create_obj_with_translation()]
            plugin.save()
            return plugin

        self._test_plugin_languages(
            plugin_type='EventListCMSPlugin',
            populate_func=populate_event_list_plugin)

    @mock.patch('aldryn_events.managers.timezone')
    def test_upcoming_events_plugin_languages(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2012, 1, 1)

        def populate_upcoming_events_plugin(plugin):
            self.create_obj_with_translation(
                start_date=tz_datetime(2017, 1, 1),
                publish_at=tz_datetime(2000, 1, 1),
            )
            return plugin

        self._test_plugin_languages(
            plugin_type='UpcomingPlugin',
            populate_func=populate_upcoming_events_plugin)

    @mock.patch('aldryn_events.managers.timezone')
    def test_upcoming_plugin_for_future(self, timezone_mock):
        """
        Test the upcoming events plugin
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        evpage = api.create_page(
            title='Events en', template=self.template, language='en',
            published=True,
            parent=self.create_root_page(),
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 1)
        )
        api.create_title('de', 'Events de', evpage)
        evpage.publish('en')
        evpage.publish('de')
        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
            publication_date=tz_datetime(2014, 1, 1)

        )
        api.create_title('de', 'Home de', page)
        ph = page.placeholders.get(slot='content')
        api.add_plugin(ph, 'UpcomingPlugin', 'en', app_config=self.app_config)
        api.add_plugin(ph, 'UpcomingPlugin', 'de', app_config=self.app_config)
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
            response = self.client.get(page.get_absolute_url('en'))
            rendered['en'] = response.content.decode('utf-8')
        with force_language('de'):
            response = self.client.get(page.get_absolute_url('de'))
            rendered['de'] = response.content.decode('utf-8')

        for i in range(1, 6):
            for lang in ['en', 'de']:
                text = 'event' if lang == 'en' else 'ereignis'
                name = '{0} {1} {2}'.format(text, i, lang)
                expected_slug = '{0}-{1}-{2}/'.format(text, i, lang)
                apphook_url = self.get_apphook_url(language=lang)
                url = '{0}{1}'.format(apphook_url, expected_slug)
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
    def test_upcoming_plugin_with_not_existing_ns(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        self.create_base_pages()
        new_config = EventsConfig.objects.create(namespace='new_namespace')
        page = api.create_page('Plugin test en', self.template, 'en',
                               published=True, slug='plugin-test-en')
        api.create_title('de', 'Plugin test de', page)
        ph = page.placeholders.get(slot='content')
        api.add_plugin(ph, 'UpcomingPlugin', 'en', app_config=new_config)
        api.add_plugin(ph, 'UpcomingPlugin', 'de', app_config=new_config)
        page.publish('en')
        page.publish('de')

        with force_language('en'):
            event = Event.objects.create(
                title='Test event namespace',
                slug='test-event-namespace',
                start_date=tz_datetime(2014, 1, 10),
                publish_at=tz_datetime(2014, 1, 1),
                app_config=new_config
            )
        event.create_translation(
            'de',
            title='Test event namespace de',
            slug='test-event-namespace-de')
        for language in ('en', 'de'):
            page_url = page.get_absolute_url(language)
            response = self.client.get(page_url)
            self.assertEqual(response.status_code, 200)

    @mock.patch('aldryn_events.managers.timezone')
    def test_calendar_plugin_with_not_existing_ns(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        self.create_base_pages()
        new_config = EventsConfig.objects.create(namespace='new_namespace')
        page = api.create_page('Plugin test en', self.template, 'en',
                               published=True, slug='plugin-test-en')
        api.create_title('de', 'Plugin test de', page)
        ph = page.placeholders.get(slot='content')
        api.add_plugin(ph, 'CalendarPlugin', 'en', app_config=new_config)
        api.add_plugin(ph, 'CalendarPlugin', 'de', app_config=new_config)
        page.publish('en')
        page.publish('de')

        with force_language('en'):
            event = Event.objects.create(
                title='Test event namespace',
                slug='test-event-namespace',
                start_date=tz_datetime(2014, 1, 10),
                publish_at=tz_datetime(2014, 1, 1),
                app_config=new_config
            )
        event.create_translation(
            'de',
            title='Test event namespace de',
            slug='test-event-namespace-de')
        for language in ('en', 'de'):
            page_url = page.get_absolute_url(language)
            response = self.client.get(page_url)
            self.assertEqual(response.status_code, 200)

    @mock.patch('aldryn_events.managers.timezone')
    def test_upcoming_plugin_for_past(self, timezone_mock):
        """
        Test the upcoming events plugin for past entries
        """
        timezone_mock.now.return_value = tz_datetime(2014, 7, 6, 12)
        evpage = api.create_page(
            title='Events en', template=self.template, language='en',
            published=True,
            apphook='EventListAppHook',
            parent=self.create_root_page(),
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 1, 1)
        )
        api.create_title('de', 'Events de', evpage)
        evpage.publish('en')
        evpage.publish('de')
        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
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
        start_date = tz_datetime(2014, 6, 29)
        start_time = start_date.now().time()
        e0 = Event.objects.filter(start_date=start_date)[0]
        e0.start_time = start_time
        e0.save()
        # Test plugin rendering for both languages in a forloop. I don't
        # like it but save lot of text space since we test for 5 entries
        rendered = {}
        with force_language('en'):
            response = self.client.get(page.get_absolute_url('en'))
            rendered['en'] = response.content.decode('utf-8')
        with force_language('de'):
            response = self.client.get(page.get_absolute_url('de'))
            rendered['de'] = response.content.decode('utf-8')

        for i in range(1, 6):
            for lang in ['en', 'de']:
                text = 'event' if lang == 'en' else 'ereignis'
                name = '{0} {1} {2}'.format(text, i, lang)
                expected_slug = '{0}-{1}-{2}/'.format(text, i, lang)
                apphooh_url = self.get_apphook_url(language=lang)
                url = '{0}{1}'.format(apphooh_url, expected_slug)
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
        self.create_base_pages()
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
        apphook_urls = {}
        for language in ('de', 'en'):
            with force_language(language):
                page_url = page.get_absolute_url()
                plugin = plugins[language]
                # prepare apphook urls with respect to language
                namespace = plugin.app_config.namespace
                apphook_urls[language] = self.get_apphook_url(
                    namespace=namespace)
                plugin_url = "{0}?plugin_pk={1}".format(
                    calendar_url(2014, 2, language, namespace), plugin.pk)
                rendered[language] = {
                    'p1': force_text(self.client.get(page_url).content),
                    'p2': force_text(self.client.get(plugin_url).content),
                }

        # expected html patterns
        html_p1 = ('<td class="events"><a href="{0}2014/1/29/">'
                   '29</a></td>')
        html_p2 = ('<td class="events"><a href="{0}2014/2/10/">'
                   '10</a></td>')

        message = ('Expected html `{0}` not found on rendered plugin for '
                   'language "{1}"')

        for language in ('de', 'en'):
            rendered_html_p1 = html_p1.format(apphook_urls[language])
            self.assertIn(
                rendered_html_p1, rendered[language]['p1'],
                message.format(rendered_html_p1, language)
            )
            rendered_html_p2 = html_p2.format(apphook_urls[language])
            self.assertIn(
                rendered_html_p2, rendered[language]['p2'],
                message.format(rendered_html_p2, language)
            )


class LanguageFallbackMixin(object):

    def setup_pages(self, multilang=False):
        root_page = self.create_root_page()
        app_page = self.create_base_pages(multilang=multilang)
        return root_page, app_page

    def create_de_only_event(self, date_start=None, date_end=None):
        if date_start is None:
            date_start = tz_datetime(2014, 1, 1, 9)
        if date_end is None:
            date_end = tz_datetime(2014, 1, 2, 9)
        event_de = self.create_event(de={
            'title': 'German event only',
            'start_date': date_start,
            'end_date': date_end,
            'publish_at': tz_datetime(2014, 1, 1, 9),
        })
        return event_de


class TestEventListPluginFallback(LanguageFallbackMixin, EventBaseTestCase):
    @mock.patch('aldryn_events.managers.timezone')
    def test_a_event_list_plugin_with_en(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2, 12)
        root_page, app_page = self.setup_pages(multilang=False)
        event_de = self.create_de_only_event()

        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'EventListCMSPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.events = [event_de]
        root_page.publish('en')
        with force_language('en'):
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'German event only')

    @mock.patch('aldryn_events.managers.timezone')
    def test_b_event_list_plugin_with_en_and_de(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2, 12)
        root_page, app_page = self.setup_pages(multilang=True)
        event_de = self.create_de_only_event()

        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'EventListCMSPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.events = [event_de]
        root_page.publish('en')
        with force_language('en'):
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'German event only')


class TestEventPastEventsPluginFallback(LanguageFallbackMixin,
                                        EventBaseTestCase):
    @mock.patch('aldryn_events.managers.timezone')
    def test_a_event_upcoming_past_plugin_with_en(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 2, 6, 12)
        root_page, app_page = self.setup_pages(multilang=False)
        self.create_de_only_event()

        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'UpcomingPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.past_events = True
        plugin_en.save()
        root_page.publish('en')
        with force_language('en'):
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'German event only')

    @mock.patch('aldryn_events.managers.timezone')
    def test_b_event_upcoming_past_plugin_with_en_and_de(self, timezone_mock):
        timezone_mock.now.return_value = tz_datetime(2014, 2, 6, 12)
        root_page, app_page = self.setup_pages(multilang=True)
        self.create_de_only_event()

        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'UpcomingPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.past_events = True
        plugin_en.save()
        root_page.publish('en')
        with force_language('en'):
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'German event only')


class TestCalendarPluginFallback(LanguageFallbackMixin, EventBaseTestCase):

    def get_list_by_day_url(self, app_config, date):
        kwargs = {
            'year': date.year,
            'month': date.month,
            'day': date.day}
        url = reverse(
            '{0}:events_list-by-day'.format(app_config.namespace),
            kwargs=kwargs)
        return url

    def test_a_calendar_plugin_with_en(self):
        root_page, app_page = self.setup_pages(multilang=False)
        now = datetime.date.today()
        today = tz_datetime(year=now.year, month=now.month, day=now.day)
        tomorrow = today + datetime.timedelta(days=1)
        event_de = self.create_de_only_event(date_start=today,
                                             date_end=tomorrow)
        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'CalendarPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.save()
        root_page.publish('en')
        with force_language('en'):
            date_view_url = self.get_list_by_day_url(event_de.app_config,
                                                     event_de.start_date)
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, date_view_url)

    def test_b_calendar_plugin_with_en_and_de(self):
        root_page, app_page = self.setup_pages(multilang=True)
        now = datetime.date.today()
        today = tz_datetime(year=now.year, month=now.month, day=now.day)
        tomorrow = today + datetime.timedelta(days=1)
        event_de = self.create_de_only_event(date_start=today,
                                             date_end=tomorrow)

        ph = root_page.placeholders.get(slot='content')
        plugin_en = api.add_plugin(
            ph, 'CalendarPlugin', 'en', app_config=self.app_config,
        )
        plugin_en.save()
        root_page.publish('en')
        with force_language('en'):
            date_view_url = self.get_list_by_day_url(event_de.app_config,
                                                     event_de.start_date)
            response = self.client.get(root_page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, date_view_url)
