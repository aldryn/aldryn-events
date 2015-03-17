# -*- coding: utf-8 -*-
import random
import string
from cms.utils.i18n import force_language

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import RequestFactory, TransactionTestCase
from django.utils.timezone import get_current_timezone

from cms import api
from cms.middleware.toolbar import ToolbarMiddleware
from cms.utils import get_cms_setting
from datetime import datetime

from aldryn_events.models import EventsConfig, Event


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


def rand_str(prefix=u'', length=23, chars=string.ascii_letters):
    return prefix + u''.join(random.choice(chars) for _ in range(length))


class EventBaseTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        super(EventBaseTestCase, self).setUp()
        self.app_config = EventsConfig.objects.create(
            namespace='aldryn_events'
        )
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]

    def tearDown(self):
        super(EventBaseTestCase, self).tearDown()
        self.app_config.delete()
        cache.clear()

    def create_root_page(self, publication_date=None):
        root_page = api.create_page(
            'root page', self.template, self.language, published=True,
            publication_date=publication_date
        )
        api.create_title('de', 'root page de', root_page)
        root_page.publish('en')
        root_page.publish('de')
        return root_page.reload()

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
        return Event.objects.language('en').get(pk=event.pk)

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
