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


***************
``settings.py``
***************

In your project's ``settings.py`` make sure you have all of::

    'aldryn_apphooks_config',
    'aldryn_boilerplates',
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

And make sure that your other settings conform to::

    TEMPLATE_CONTEXT_PROCESSORS = [
        ...
        'aldryn_boilerplates.context_processors.boilerplate',
    ]

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        # important! place right before django.contrib.staticfiles.finders.AppDirectoriesFinder
        'aldryn_boilerplates.staticfile_finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

    TEMPLATE_LOADERS = [
        'django.template.loaders.filesystem.Loader',
        # important! place right before django.template.loaders.app_directories.Loader
        'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',
        'django.template.loaders.app_directories.Loader',
    ]

Now set the name of the boilerplate you want to use in your project::

    ALDRYN_BOILERPLATE_NAME = 'bootstrap3'

.. note::
   Note that Aldryn Events doesn't use the the traditional Django ``/templates`` and ``/static
   directories``. Instead, it employs `Aldryn Boilerplates
   <https://github.com/aldryn/aldryn-boilerplates>`_, which makes it possible to to support
   multiple different frontend schemes ('Boilerplates')and switch between them without a need for
   project-by-project file overwriting.

   Aldryn Events's templates and staticfiles will be found in named directories inside the
   ``/boilerplates`` directory.


****************************
Prepare the database and run
****************************

Now run ``python manage.py migrate`` to prepare the database for the new application, then
``python manage.py runserver``.


****************
For Aldryn users
****************

To install the addon on Aldryn, all you need to do is follow this
`installation link <https://control.aldryn.com/control/?select_project_for_addon=aldryn-events>`_
on the Aldryn Marketplace and follow the instructions.
