|PyPI Version| |Build Status| |Coverage Status|

=============
Aldryn-Events
=============

Description
~~~~~~~~~~~
A events application for Aldryn and Django CMS.

Aldryn Events support events with own start/end dates and has a simple
registration proccess to events.

--------------------
Installation & Usage
--------------------

Django CMS Requirements
~~~~~~~~~~~~~~~~~~~~~~~

This project requires Django CMS 3.0.12 or later.


Aldryn Platform Users
~~~~~~~~~~~~~~~~~~~~~

1) Choose a site you want to install the add-on to from the dashboard.

2) Go to **Apps** > **Install App**

3) Click **Install** next to the **Events** app.

4) Redeploy the site.

Manual Installation
~~~~~~~~~~~~~~~~~~~

1) Run `pip install aldryn-events`. Following packages will be installed: ::

    aldryn-apphooks-config>=0.1.4
    aldryn-boilerplates
    aldryn-common>=0.0.6
    django-appconf
    django-bootstrap3
    django-extended-choices
    django-filer
    django-parler
    django-sortedm2m
    django-standard-form>=1.1.1
    django-tablib
    djangocms-text-ckeditor
    python-dateutil

Aldryn Events support both Django 1.6 and Django 1.7. If you are using with
Django 1.6, South will be installed: ::

    South<1.1,>=1.0.2

2) Add below apps to ``INSTALLED_APPS``: ::

    INSTALLED_APPS = [
        …
        "aldryn_apphooks_config",
        "aldryn_boilerplates",
        "aldryn_common",
        "aldryn_events",
        "appconf",
        "bootstrap3",
        "django_tablib",
        "djangocms_text_ckeditor",
        "easy_thumbnails",
        "extended_choices",
        "filer",
        "parler",
        "sortedm2m",
        "standard_form"
        …
    ]

If you are using Django 1.6, add ``south`` to installed apps.

3) Configure ``aldryn-boilerplates`` (https://pypi.python.org/pypi/aldryn-
   boilerplates/).

   To use the old templates, set ``ALDRYN_BOILERPLATE_NAME='legacy'``. To use
   https://github.com/aldryn/aldryn-boilerplate-standard (recommended, will be
   renamed to ``aldryn-boilerplate-bootstrap3``) set
   ``ALDRYN_BOILERPLATE_NAME='bootstrap3'``.

4) Run migrations: ``python manage.py migrate aldryn_events``.

   NOTE: aldryn_events supports both South and Django 1.7 migrations. If using
   Django 1.7, you may need to add the following to your settings: ::

    MIGRATION_MODULES = [
       …
       # The following are for some of the depenencies.
       'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations_django',
       'filer': 'filer.migrations_django',
       …
    ]

5) Add Required Easy Thumbnail setting

   Aldryn Events requires the use of the optional "subject location" processor
   from Django Filer for Easy Thumbnails. This requires setting the
   THUMBNAIL_PROCESSORS tuple in your project's settings and explicitly omitting
   the default processor ``scale_and_crop`` and including the optional
   ``scale_and_crop_with_subject_location`` processor. For example: ::

    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        # 'easy_thumbnails.processors.scale_and_crop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
        # 'entercoms.apps.strategies.processors.reflect',
    )

   For more information on this optional processor, see the
   `documentation for Django Filer`__.

__ http://django-filer.readthedocs.org/en/latest/installation.html#subject-location-aware-cropping

6) (Re-)Start your application server.


=====
Notes
=====

Python 2.6 and django-tablib
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aldryn Events supports Python 2.6 and Python 2.7 as expected, but there is `a
bug in django-tablib with Python 2.6 that avoid to use last version of
django-tablib`__, so we need to use a `patched version`__. setup.py installs
that version for Python 2.6.


Known Issues
~~~~~~~~~~~~

Due to the way existing versions of Django work, after creating a new app-hook,
django CMS requires that the server is restarted. This is a long-standing issue.
For more information, see the `documentation for django CMS`__.

__ https://github.com/joshourisman/django-tablib/pull/37
__ https://github.com/aldryn/aldryn-apphooks-config/archive/master.zip
__ https://django-cms.readthedocs.org/en/support-3.0.x/how_to/apphooks.html#apphooks

