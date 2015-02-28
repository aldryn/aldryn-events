# -*- coding: utf-8 -*-
from importlib import import_module

import mock
import random
import string

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext
from django.test import RequestFactory
from django.test import TransactionTestCase
from cms import api
from cms.middleware.toolbar import ToolbarMiddleware
from cms.utils import get_cms_setting
from cms.utils.i18n import force_language
from datetime import datetime
from django.utils.timezone import utc

from aldryn_events.models import Event, EventsConfig


def tz_datetime(*args, **kwargs):
    return datetime(tzinfo=utc, *args, **kwargs)


def get_page_request(page, user=None, path=None, edit=False, language='en'):

    path = path or page and page.get_absolute_url()
    if edit:
        path += '?edit'
    request = RequestFactory().get(path)
    request.session = {}
    request.user = user or AnonymousUser()
    request.LANGUAGE_CODE = language
    if edit:
        request.GET = {'edit': None}
    else:
        request.GET = {'edit_off': None}
    request.current_page = page
    mid = ToolbarMiddleware()
    mid.process_request(request)
    return request


def rand_str(prefix=u'', length=23, chars=string.ascii_letters):
    return prefix + u''.join(random.choice(chars) for _ in range(length))


class EventTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.app_config, created = EventsConfig.objects.get_or_create(namespace='aldryn_events')
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.root_page = api.create_page(
            'root page', self.template, self.language, published=True
        )
        api.create_title('de', 'root page de', self.root_page)

    def tearDown(self):
        super(EventTestCase, self).tearDown()
        cache.clear()

    def create_event(self):
        with force_language('en'):
            event = Event.objects.create(
                title='Event2014', slug='open-air',
                start_date=tz_datetime(2014, 9, 10),
                publish_at=tz_datetime(2014, 1, 1, 12),
                app_config=self.app_config
            )
        event.create_translation('de', title='Ereignis', slug='im-freien')
        return Event.objects.language('en').get(pk=event.pk)

    # add events
    def new_event_from_num(self, num, start_date, end_date, publish_at):
        """ create event based on a num in both languages """
        text, text_de = 'event', 'ereignis'
        with force_language('en'):
            event = Event.objects.create(
                title='{0} {1} en'.format(text, num),
                slug='{0}-{1}-en'.format(text, num),
                app_config=self.app_config,
                start_date=start_date, end_date=end_date,
                publish_at=publish_at
            )
        event.create_translation(
            language_code='de',
            title='{0} {1} de'.format(text_de, num),
            slug='{0}-{1}-de'.format(text_de, num)
        )
        return Event.objects.language('en').get(pk=event.pk)

    @mock.patch('aldryn_events.managers.timezone')
    def test_create_event(self, timezone_mock):
        """
        We can create an event with a name in two languages
        """
        timezone_mock.now.return_value = tz_datetime(2014, 9, 9)
        self.assertEqual(Event.objects.count(), 0)
        with force_language('en'):
            event = Event.objects.create(
                title='Concert', slug='open-concert',
                start_date=tz_datetime(2014, 9, 10),
                publish_at=tz_datetime(2014, 9, 9),
                app_config=self.app_config
            )
        self.assertEqual(Event.objects.translated('en').count(), 1)
        self.assertEqual(Event.objects.translated('de').count(), 0)
        self.assertEqual(event.get_current_language(), 'en')

        event.create_translation('de', title='Konzert', slug='offene-konzert')

        self.assertEqual(Event.objects.translated('en').count(), 1)
        self.assertEqual(Event.objects.translated('de').count(), 1)

    @mock.patch('aldryn_events.managers.timezone')
    def test_event_detail_page(self, timezone_mock):
        """
        Test if proper url and event page are created
        """
        timezone_mock.now.return_value = tz_datetime(2014, 9, 1, 12)
        event = self.create_event()

        # '/events/' came from tests/urls.py, '/open-air/' from the event slug
        self.assertEqual(event.get_absolute_url(), '/en/events/open-air/')
        with force_language('en'):
            response = self.client.get(event.get_absolute_url())
        self.assertContains(response, event.title)

        event.set_current_language('de')
        # '/events/' came from tests/urls.py, '/im-freien/' from the event slug
        self.assertEqual(event.get_absolute_url(), '/de/events/im-freien/')
        with force_language('de'):
            response = self.client.get(event.get_absolute_url())
        self.assertContains(response, event.title)

    @mock.patch('aldryn_events.managers.timezone')
    def test_add_event_app_to_page(self, timezone_mock):
        """
        We add an event to the app
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        page = api.create_page(
            'Events en', self.template, 'en', slug='eventsapp', published=True,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace
        )
        api.create_title('de', 'Events de', page, slug='eventsapp')
        page.publish('en')
        page.publish('de')

        # create events
        event1 = self.create_event()
        event2 = Event.objects.language('en').create(
            title='Event2015 only english',
            start_date=tz_datetime(2014, 9, 10),
            publish_at=tz_datetime(2014, 1, 1),
            app_config=self.app_config

        )

        # test english, have 2 events
        response = self.client.get('/en/eventsapp/')
        self.assertContains(response, event1.title)
        self.assertContains(response, event1.get_absolute_url())
        self.assertContains(response, event2.title)
        self.assertContains(response, event2.get_absolute_url())

        # test german, have 1 event, event 2 is only english
        event1.set_current_language('de')
        response = self.client.get('/de/eventsapp/')
        self.assertContains(response, event1.title)
        self.assertContains(response, event1.get_absolute_url())
        self.assertNotContains(response, event2.title)
        self.assertNotContains(response, event2.get_absolute_url())

    @mock.patch('aldryn_events.managers.timezone')
    def test_event_list_plugin(self, timezone_mock):
        """
        We add an event to the Event Plugin and look it up
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2, 12),

        # add events
        event1 = self.create_event()
        with force_language('en'):
            event2 = Event.objects.create(
                title='Event2014 only english',
                start_date=tz_datetime(2014, 1, 29),
                publish_at=tz_datetime(2014, 1, 1, 12),
                app_config=self.app_config
            )
        page = api.create_page(
            'Events en', self.template, 'en', published=True,
            parent=self.root_page,
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
        This plugin should show a link to event list page on days that has events
        """
        timezone_mock.now.return_value = tz_datetime(2014, 1, 2)
        plugin_timezone_mock.now.return_value = tz_datetime(2014, 1, 2)

        page = api.create_page(
            'Home en', self.template, 'en', published=True, slug='home',
        )
        api.create_title('de', 'Home de', page)
        ph = page.placeholders.get(slot='content')
        api.add_plugin(ph, 'CalendarPlugin', 'en', app_config=self.app_config)
        api.add_plugin(ph, 'CalendarPlugin', 'de', app_config=self.app_config)
        page.publish('en')
        page.publish('de')

        for i in range(1, 7):
            self.new_event_from_num(
                i,
                start_date=tz_datetime(2014, 1, 29, 12),
                end_date=tz_datetime(2014, 2, 5, 12),
                publish_at=tz_datetime(2014, 1, 1, 12)
            )

        # Test plugin rendering for both languages in a forloop. I don't
        # like it but save lot of text space since we test for 5 entries
        rendered = {}
        with force_language('en'):
            rendered['en'] = self.client.get('/en/home/').content
        with force_language('de'):
            rendered['de'] = self.client.get('/de/home/').content

        html = ('<td class="events"><a href="/{0}/events/2014/1/29/">'
                '29</a></td>')
        self.assertIn(
            html.format('de'), rendered['de'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html.format('de'), 'DE')
        )
        self.assertIn(
            html.format('en'), rendered['en'],
            'Expected html `{0}` not found on rendered plugin for '
            'language "{1}"'.format(html.format('en'), 'EN')
        )

    def test_event_fill_slug_with_manager_create(self):
        event = Event.objects.create(
            title='show me the slug',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        self.assertEqual(event.slug, 'show-me-the-slug')

    def test_event_fill_slug_with_instance_save(self):
        event = Event(
            title='show me the slug',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        event.save()
        self.assertEqual(event.slug, 'show-me-the-slug')

    def test_event_not_overwrite_slug_with_manager_create(self):
        event = Event.objects.create(
            title='show me the slug',
            slug='gotchaa',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        self.assertEqual(event.slug, 'gotchaa')

    def test_event_not_overwrite_slug_with_instance_save(self):
        event = Event(
            title='show me the slug', slug='gotchaa',
            start_date=tz_datetime(2015, 2, 4),
            app_config=self.app_config
        )
        event.save()
        self.assertEqual(event.slug, 'gotchaa')


class RegistrationTestCase(TransactionTestCase):

    def tearDown(self):
        super(RegistrationTestCase, self).tearDown()
        cache.clear()

    @mock.patch('aldryn_events.models.timezone')
    def test_submit_registration(self, timezone_mock):
        app_config = EventsConfig.objects.create(namespace='aldryn_events')
        timezone_mock.now.return_value = tz_datetime(2015, 2, 5, 9)

        with force_language('en'):
            event = Event.objects.create(
                id=5,
                title='Event2014', slug='open-air',
                start_date=tz_datetime(2015, 2, 7),
                publish_at=tz_datetime(2015, 2, 2, 9),
                registration_deadline_at=tz_datetime(2015, 2, 7),
                enable_registration=True,
                app_config=app_config
            )
        event.event_coordinators.create(name='The big boss',
                                        email='theboss@gmail.com')
        event.create_translation('de', title='Ereignis', slug='im-freien')
        event.set_current_language('en')
        data = {
            'salutation': 'mrs',
            'company': 'any',
            'first_name': 'Felipe',
            'last_name': 'Somename',
            'address': 'My Street, 77, Brazil, Earth, Solar system',
            'address_zip': '00000-000',
            'address_city': u'São Paulo',
            'phone': '+55 (11) 1234-5678',
            'mobile': '+55 (11) 1234-5678',
            'email': 'myemail@gmail.com',
            'message': "I'm testing you"
        }
        response = self.client.post(
            event.get_absolute_url(), data
        )

        self.assertRedirects(response, event.get_absolute_url())

        # test if emails was sent
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            'Thank you for signing up to "{0}"'.format(event.title)
        )
        self.assertEqual(['myemail@gmail.com'], mail.outbox[0].recipients())
        self.assertEqual(
            mail.outbox[1].subject,
            'new registration for "{0}"'.format(event.title)
        )
        self.assertEqual(['theboss@gmail.com'], mail.outbox[1].recipients())

        # test if registration is really on db
        registration = event.registration_set.get()
        for k, v in data.items():
            self.assertEqual(getattr(registration, k), v)

    @mock.patch('aldryn_events.models.timezone')
    def test_reset_registration(self, timezone_mock):
        app_config = EventsConfig.objects.create(namespace='aldryn_events')
        timezone_mock.now.return_value = tz_datetime(2015, 2, 5, 9)

        with force_language('en'):
            event = Event.objects.create(
                title='Event2014', slug='open-air',
                start_date=tz_datetime(2015, 2, 7),
                publish_at=tz_datetime(2015, 2, 2, 9),
                registration_deadline_at=tz_datetime(2015, 2, 7),
                enable_registration=True,
                app_config=app_config
            )
        event.create_translation('de', title='Ereignis2014', slug='im-freien')
        event.event_coordinators.create(name='The big boss',
                                        email='theboss@gmail.com')
        event.registration_set.create(
            salutation='mrs',
            company='any',
            first_name='Felipe',
            last_name='Somename',
            address='My Street, 77, Brazil, Earth, Solar system',
            address_zip='00000-000',
            address_city=u'São Paulo',
            phone='+55 (11) 1234-5678',
            mobile='+55 (11) 1234-5678',
            email='myemail@gmail.com',
            message="I'm testing you"
        )
        with force_language('en'):
            reset_url = reverse(
                'aldryn_events:events_registration_reset',
                kwargs={'slug': event.slug},
                current_app=app_config.namespace
            )
        custom_settings = {
            'SESSION_ENGINE': 'django.contrib.sessions.backends.db'
        }
        with self.settings(**custom_settings):
            # create the session
            engine = import_module(settings.SESSION_ENGINE)
            session = engine.SessionStore()
            session['registered_events'] = [event.pk]
            session.save()

            # Set the cookie to represent the session.
            session_cookie = settings.SESSION_COOKIE_NAME
            self.client.cookies[session_cookie] = session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': settings.SESSION_COOKIE_DOMAIN,
                'secure': settings.SESSION_COOKIE_SECURE or None,
                'expires': None,
            }
            self.client.cookies[session_cookie].update(cookie_data)

            response = self.client.post(reset_url, {})

        # load session data modified in request
        del session._session_cache  # need to remove it so updated data is loaded
        self.assertEqual(session.get('registered_events'), [])
        self.assertRedirects(response, event.get_absolute_url())

    @mock.patch('aldryn_events.managers.timezone')
    def test_unattached_namespace(self, manager_timezone_mock):
        manager_timezone_mock.now.return_value = tz_datetime(2015, 2, 2, 10)
        event1 = Event.objects.create(
            title='Event2015 current namespace',
            slug='open-air',
            start_date=tz_datetime(2015, 2, 7),
            publish_at=tz_datetime(2015, 2, 2, 9),
            registration_deadline_at=tz_datetime(2015, 2, 7),
            enable_registration=True,
            app_config=EventsConfig.objects.create(namespace='aldryn_events')
        )
        event2 = Event.objects.create(
            title='Event new namespace', slug='open-air-new-namespace',
            start_date=tz_datetime(2015, 2, 7),
            publish_at=tz_datetime(2015, 2, 2, 9),
            registration_deadline_at=tz_datetime(2015, 2, 7),
            enable_registration=True,
            app_config=EventsConfig.objects.create(namespace='another')
        )
        response = self.client.get(reverse('aldryn_events:events_list'))
        self.assertContains(response, event1.title)
        self.assertNotContains(response, event2.title)
