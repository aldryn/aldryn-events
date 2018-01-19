#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from distutils.version import LooseVersion
from cms import __version__ as cms_string_version

cms_version = LooseVersion(cms_string_version)


def noop_gettext(s):
    return s


gettext = noop_gettext


HELPER_SETTINGS = {
    'TIME_ZONE': 'UTC',
    'INSTALLED_APPS': [
        'aldryn_apphook_reload',  # for tests
        'aldryn_apphooks_config',
        'aldryn_common',
        'aldryn_translation_tools',
        'appconf',
        'bootstrap3',
        'djangocms_text_ckeditor',
        'easy_thumbnails',
        'extended_choices',
        'filer',
        'mptt',
        'parler',
        'sortedm2m',
        'standard_form',
        'django_tablib',
        'aldryn_events',
    ],
    'CMS_PERMISSION': True,
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
    ),
    'PARLER_LANGUAGES': {
        1: [
            {
                'code': u'en',
                'fallbacks': [u'de'],
                'hide_untranslated': False
            },
            {
                'code': u'de',
                'fallbacks': [u'en'],
                'hide_untranslated': False
            }
        ],
        'default': {
            'code': u'en',
            'fallbacks': [u'en'],
            'hide_untranslated': False}
    },
    'PARLER_ENABLE_CACHING': False,
    'CMS_LANGUAGES': {
        'default': {
            'public': True,
            'hide_untranslated': False,
            'fallbacks': ['en']

        },
        1: [
            {
                'public': True,
                'code': 'en',
                'fallbacks': [u'de'],
                'hide_untranslated': False,
                'name': gettext('en'),
                'redirect_on_fallback': True,
            },
            {
                'public': True,
                'code': 'de',
                'fallbacks': [u'en'],
                'hide_untranslated': False,
                'name': gettext('de'),
                'redirect_on_fallback': True,
            },
        ],
    },
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'DEBUG': True,
    # 'TEMPLATE_DEBUG': True,
    'ALDRYN_EVENTS_USER_REGISTRATION_EMAIL': True,
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_events')


if __name__ == "__main__":
    run()
