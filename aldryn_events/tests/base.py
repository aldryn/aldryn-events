# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
import string

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.urlresolvers import reverse, clear_url_caches

from django.test import RequestFactory, TransactionTestCase
from django.utils.timezone import get_current_timezone

from cms import api
from cms.apphook_pool import apphook_pool
from cms.appresolver import clear_app_resolvers
from cms.middleware.toolbar import ToolbarMiddleware
from cms.utils.i18n import force_language
from cms.exceptions import AppAlreadyRegistered
from cms.utils import get_cms_setting
from datetime import datetime

from djangocms_helper.utils import create_user

from aldryn_events.cms_apps import EventListAppHook
from aldryn_events.models import EventsConfig, Event


APP_MODULE = 'aldryn_events.cms_apps'


def tz_datetime(*args, **kwargs):
    """ Return datetime with arguments in UTC timezone """
    return datetime(tzinfo=get_current_timezone(), *args, **kwargs)


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


def rand_str(prefix='', length=23, chars=string.ascii_letters):
    return prefix + ''.join(random.choice(chars) for _ in range(length))


class EventTestCaseSetupMixin(object):

    def setUp(self):
        super(EventTestCaseSetupMixin, self).setUp()
        # since aldryn_events namespace is created inside of a migration 0016
        # use something different for test purposes
        self.app_config = EventsConfig.objects.create(
            namespace='events_test_namespace'
        )
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]

    def tearDown(self):
        """
        Do a proper cleanup, delete everything what is preventing us from
        clean environment for tests.
        :return: None
        """
        self.app_config.delete()
        self.reset_all()
        cache.clear()

    def reset_apphook_cmsapp(self):
        """
        For tests that should not be polluted by previous setup we need to
        ensure that app hooks are reloaded properly. One of the steps is to
        reset the relation between EventListAppHook and EventsConfig
        """
        app_config = getattr(EventListAppHook, 'app_config', None)
        if (app_config and
                getattr(app_config, 'cmsapp', None)):
            delattr(EventListAppHook.app_config, 'cmsapp')
        if getattr(EventsConfig, 'cmsapp', None):
            delattr(EventsConfig, 'cmsapp')

    def reset_all(self):
        """
        Reset all that could leak from previous test to current/next test.
        :return: None
        """
        self.delete_app_module()
        self.reload_urls()
        self.apphook_clear()

    def delete_app_module(self):
        """
        Remove APP_MODULE from sys.modules. Taken from cms.
        :return: None
        """
        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]

    def apphook_clear(self):
        """
        Clean up apphook_pool and sys.modules. Taken from cms with slight
        adjustments and fixes.
        :return: None
        """
        try:
            apphooks = apphook_pool.get_apphooks()
        except AppAlreadyRegistered:
            # there is an issue with discover apps, or i'm using it wrong.
            # setting discovered to True solves it. Maybe that is due to import
            # from aldryn_events.cms_apps which registers EventListAppHook
            apphook_pool.discovered = True
            apphooks = apphook_pool.get_apphooks()

        for name, label in list(apphooks):
            if apphook_pool.apps[name].__class__.__module__ in sys.modules:
                del sys.modules[apphook_pool.apps[name].__class__.__module__]
        apphook_pool.clear()
        self.reset_apphook_cmsapp()

    def reload_urls(self):
        """
        Clean up url related things (caches, app resolvers, modules).
        Taken from cms.
        :return: None
        """
        clear_app_resolvers()
        clear_url_caches()
        url_modules = [
            'cms.urls',
            'aldryn_events.urls',
            settings.ROOT_URLCONF
        ]

        for module in url_modules:
            if module in sys.modules:
                del sys.modules[module]

    def create_super_user(self, user_name, user_password):

        super_user = create_user(
            username=user_name,
            email='test@example.com',
            password=user_password,
            is_superuser=True,
        )
        return super_user


class EventBaseTestCase(EventTestCaseSetupMixin, TransactionTestCase):

    def create_root_page(self, publication_date=None):
        root_page = api.create_page(
            'root page', self.template, self.language, published=True,
            publication_date=publication_date
        )
        api.create_title('de', 'root page de', root_page)
        root_page.publish('en')
        root_page.publish('de')
        return root_page.reload()

    def create_base_pages(self, multilang=True):
        root_page = self.create_root_page(
            publication_date=tz_datetime(2014, 6, 8)
        )
        # we cannot extract this to setUp because of mocking
        # but having self.root_page would be useful.
        if getattr(self, 'root_page', None) is None:
            self.root_page = root_page

        page = api.create_page(
            title='Events en', template=self.template, language='en',
            published=True,
            parent=root_page,
            apphook='EventListAppHook',
            apphook_namespace=self.app_config.namespace,
            publication_date=tz_datetime(2014, 6, 8)
        )
        page.publish('en')
        if multilang:
            api.create_title('de', 'Events de', page)
            page.publish('de')
        return page.reload()

    def create_event(self, de={}, **en):
        """
        Create events in english and german. Use **en because normaly
        for very simple tests we just create events in english.
        """
        if not en and not de:
            raise ValueError(
                "You must provide data for english and/or german!"
            )
        if en:
            en.setdefault('app_config', self.app_config)
            with force_language('en'):
                event = Event.objects.create(**en)
        if de:
            if not en:
                de.setdefault('app_config', self.app_config)
                with force_language('de'):
                    event = Event.objects.language('de').create(**de)
            else:
                event.create_translation('de', **de)
        return Event.objects.get(pk=event.pk)

    def create_default_event(self):
        en = {
            'title': 'Event2014',
            'slug': 'open-air',
            'start_date': tz_datetime(2014, 9, 10),
            'publish_at': tz_datetime(2014, 9, 10, 9),
            'app_config': self.app_config
        }
        de = {
            'title': 'Ereignis',
            'slug': 'im-freien'
        }
        return self.create_event(de=de, **en)

    def make_default_values_with_new_dates(self, date_values, num=None):
        """
        Prepare a dictionary with changed text values, and with provided dates.
        Num is used to generate test values.
        Acceptable date Formats:
             2015-07-01, 07/01/2015, 07/01/15
        Acceptable time Formats: (from admin form hint):
            09:47:10, 09:47:10.551027, 09:47
        Expects date_values to be dict in the following format or mix-ups:
        {
            'start_date': '2015-01-01',
            'end_date': '2015-01-01',
            'start_time': '09:47:10',
            'end_time': '09:47:10'
        }
        """
        if num is None:
            num = random.randint(0, 9999999)
        defaut_event_values = {
            'title': 'Default event test {0}'.format(num),
            'app_config': self.app_config,
            'short_description': 'Lorem ipsum blah blah {0}'.format(num),
        }
        defaut_event_values.update(date_values)
        return defaut_event_values

    def get_apphook_url(self, namespace=None, language=None):
        """
        Returns url for default view with pattern '^$' which is a
        base url for our application. Right now 'events_list' is
        considered as default view.
        """
        DEFAULT_VIEW = 'events_list'

        if namespace is None:
            namespace = self.app_config.namespace
        # if language is not provided then leave control over language to
        # caller
        if language is None:
            return reverse('{0}:{1}'.format(namespace, DEFAULT_VIEW))
        # otherwise force it for cases with parler switch_language which
        # seems to affect only parler internals
        with force_language(language):
            return reverse('{0}:{1}'.format(namespace, DEFAULT_VIEW))
