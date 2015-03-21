=============
Aldryn-Events
=============

.. image:: https://magnum.travis-ci.com/aldryn/aldryn-events.svg?token=2aLiyxMhwop2hnmajHuq&branch=master
    :target: https://magnum.travis-ci.com/aldryn/aldryn-events

.. image:: https://img.shields.io/coveralls/aldryn/aldryn-events.svg
  :target: https://coveralls.io/r/aldryn/aldryn-events

**do not add an application namespace using this app**

# To Do
    Redo translations.
    Look into placeholder issues in frontend.
    Add backwards compatibility with CMS 2.4


Installation
============

Aldryn Platform Users
---------------------

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``Events`` app.

Redeploy the site.

Manuall Installation
--------------------

::

    pip install aldryn-events

Add ``aldryn_events`` to ``INSTALLED_APPS``.

Configure ``aldryn-boilerplates`` (https://pypi.python.org/pypi/aldryn-boilerplates/).

To use the old templates, set ``ALDRYN_BOILERPLATE_NAME='legacy'``.
To use https://github.com/aldryn/aldryn-boilerplate-standard (recommended, will be renamed to
``aldryn-boilerplate-bootstrap3``) set ``ALDRYN_BOILERPLATE_NAME='bootstrap3'``.
