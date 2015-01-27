#!/usr/bin/env python
# -*- coding: utf-8 -*-

HELPER_SETTINGS = {
    'TIME_ZONE': 'Europe/Zurich',
    'INSTALLED_APPS': [
        'filer',
        'easy_thumbnails',
    ],
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
}

def run():
    from djangocms_helper import runner
    runner.cms('aldryn_events')

if __name__ == "__main__":
    run()
