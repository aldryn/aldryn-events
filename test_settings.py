#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from django import get_version


class DisableMigrations(dict):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


class DisableMigrations(dict):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

gettext = lambda s: s

HELPER_SETTINGS = {
    # 'ROOT_URLCONF': 'aldryn_events.tests.urls',
    'TIME_ZONE': 'UTC',
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
        'aldryn_apphooks_config'
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
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    # 'MIGRATION_MODULES ': {
    #     'filer': 'filer.migrations_django',
    # },
    # Disable migrations so tests runs really faster
    # Source: https://gist.github.com/c-rhodes/cebe9d4619125949dff8
    'MIGRATION_MODULES': DisableMigrations(),  # disable migration for DJ 1.7 in tests
    'SOUTH_TESTS_MIGRATE': False,  # disable migration for DJ < 1.6 in tests
    # 'DEBUG': True,
    # 'TEMPLATE_DEBUG': True,
    'ALDRYN_EVENTS_USER_REGISTRATION_EMAIL': True,
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/aldryn_events_test_cache',
        }
    }
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_events')

if __name__ == "__main__":
    run()
