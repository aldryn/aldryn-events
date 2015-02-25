#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

class DisableMigrations(dict):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


gettext = lambda s: s
HELPER_SETTINGS = {
    'ROOT_URLCONF': 'aldryn_events.tests.urls',
    'TIME_ZONE': 'Europe/Zurich',
    'INSTALLED_APPS': [
        'mptt',
        'parler',
        'hvad',
        'filer',
        'easy_thumbnails',
        'django_tablib',
        'sortedm2m',
        'standard_form',
        'aldryn_events',
    ],
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
    ),
    'PARLER_LANGUAGES': {
        1: (
            {'code': 'en',},
            {'code': 'de',},
        ),
        'default': {
            'hide_untranslated': False,
        }
    },
    'CMS_LANGUAGES': {
        'default': {
            'public': True,
            'hide_untranslated': False,
            'redirect_on_fallback': True,
        },
        1: [
            {
                'public': True,
                'code': 'en',
                'hide_untranslated': False,
                'name': gettext('en'),
                'redirect_on_fallback': True,
            },
            {
                'public': True,
                'code': 'de',
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
    # 'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    # 'MIGRATION_MODULES ': {
    #     'filer': 'filer.migrations_django',
    # },
    'MIGRATION_MODULES': DisableMigrations(),
    'SOUTH_TESTS_MIGRATE': True,
    # 'DEBUG': True,
    # 'TEMPLATE_DEBUG': True,
    'ALDRYN_EVENTS_USER_REGISTRATION_EMAIL': True
}

# if 'test' in sys.argv:
#     HELPER_SETTINGS['DATABASES'] = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
#             'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
#        }
#     }


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_events')

if __name__ == "__main__":
    run()
