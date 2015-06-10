#!/usr/bin/env python

import sys
import os

import django

_args = list(sys.argv)
_args.pop(_args.index('runtests.py'))

cmd = 'coverage run `which djangocms-helper` aldryn_events test --cms --extra-settings=test_settings %s'
cmd = cmd % ' '.join(_args)

if django.VERSION[:2] < (1, 6):
    cmd += ' --runner=discover_runner.DiscoverRunner'

sys.exit(os.system(cmd))
