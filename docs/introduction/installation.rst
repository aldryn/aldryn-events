############
Installation
############


*******************
Installing packages
*******************

We'll assume you have a django CMS (version 3.x) project up and running.

If you need to set up a new django CMS project, follow the instructions in the `django CMS tutorial
<http://docs.django-cms.org/en/develop/introduction/install.html>`_.

Then run either::

    pip install aldryn-events

or to install from the latest source tree::

    pip install -e git+https://github.com/aldryn/aldryn-events.git#egg=aldryn-events


********************
Edit ``settings.py``
********************

In your project's ``settings.py`` make sure you have all of::

    'aldryn_apphooks_config',
    'aldryn_boilerplates',
    'aldryn_translation_tools',
    'aldryn_common',
    'aldryn_events',
    'appconf',
    'bootstrap3',
    'django_tablib',
    'djangocms_text_ckeditor',
    'easy_thumbnails',
    'extended_choices',
    'filer',
    'parler',
    'sortedm2m',
    'standard_form',

listed in ``INSTALLED_APPS``, *after* ``'cms'``.


Aldryn Boilerplates
===================

This application uses (and will install) `Aldryn Boilerplates <https://github.com/aldryn/aldryn-boilerplates>`_,
which requires some basic configuration to get you started.

.. note::

    If you are using Django 1.8 please note the `configuration instructions for Aldryn Boilerplates
    <https://github.com/aldryn/aldryn-boilerplates#django-18>`_.

Edit your settings so that they conform to::

    TEMPLATE_CONTEXT_PROCESSORS = [
        ...
        'aldryn_boilerplates.context_processors.boilerplate',
        ...
    ]

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        # important - place immediately before AppDirectoriesFinder
        'aldryn_boilerplates.staticfile_finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

    TEMPLATE_LOADERS = [
        'django.template.loaders.filesystem.Loader',
        # important! place right before django.template.loaders.app_directories.Loader
        'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',
        'django.template.loaders.app_directories.Loader',
    ]

Now set the name of the boilerplate you'll use in your project::

    ALDRYN_BOILERPLATE_NAME = 'bootstrap3'

.. note::
   Note that Aldryn Events doesn't use the the traditional Django ``/templates`` and ``/static
   directories``. Instead, it employs `Aldryn Boilerplates
   <https://github.com/aldryn/aldryn-boilerplates>`_, which makes it possible to to support
   multiple different frontend schemes ('Boilerplates')and switch between them without the need for
   project-by-project file overwriting.

   Aldryn Events's templates and static files will be found in named directories in the
   ``/boilerplates`` directory.


Filer
=====

Aldryn Events also depends on Filer, be sure to follow
`Filer's installation instructions <http://django-filer.readthedocs.org/en/latest/installation.html>`_.
To get up and running quickly, make sure you adapt your settings to include the
``filer.thumbnail_processors.scale_and_crop_with_subject_location`` thumbnail processor: ::

    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        # 'easy_thumbnails.processors.scale_and_crop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )


****************************
Prepare the database and run
****************************

Now run ``python manage.py migrate`` to prepare the database for the new
application, then ``python manage.py runserver``.


****************
For Aldryn users
****************

On the Aldryn platform, the Addon is available from the `Marketplace
<http://www.aldryn.com/en/marketplace>`_.

You can also `install Aldryn Events into any existing Aldryn project
<https://control.aldryn.com/control/?select_project_for_addon=aldryn-events>`_.
