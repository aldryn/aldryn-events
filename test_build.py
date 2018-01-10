# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import socket
import sys

from shutil import rmtree as _rmtree
from tempfile import mkdtemp, _exists

import aldryn_events

from sphinx.application import Sphinx

try:
    import enchant
except ImportError:
    enchant = None

ROOT_DIR = os.path.dirname(aldryn_events.__file__)
DOCS_DIR = os.path.abspath(os.path.join(ROOT_DIR, u'..', u'docs'))


def has_no_internet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        s.connect(('4.4.4.2', 80))
        s.send(b"hello")
    except socket.error:  # no internet
        return True
    return False


def test_build(builder_name='html', warnings=False):
    """
    Try to build docs, by default sphinx is writing its messages to std.out
    and errors to std.err.
    To test with different builders change builder_name, default is 'html'
    """
    OUT_DIR = mkdtemp()
    app = Sphinx(
        srcdir=DOCS_DIR,
        confdir=DOCS_DIR,
        outdir=OUT_DIR,
        doctreedir=OUT_DIR,
        buildername=builder_name,
        warningiserror=warnings,
    )
    app.build()
    # cleanup
    cleanup(OUT_DIR)
    return app.statuscode


def cleanup(dirname):
    """
    Delete temp directory for so that no overlap with other builds.
    """
    if _exists(dirname):
        _rmtree(dirname)


if __name__ == '__main__':
    args = {}
    if has_no_internet():
        print('Seems there is no internet, cannot test without internet...')
        sys.exit(1)
    try:
        args['builder_name'] = sys.argv[1]
    except IndexError:
        pass
    sys.exit(test_build(**args))
