############
Installation
############

If you're installing into an existing django CMS project, you can run either::

    pip install aldryn-events

or to install from the latest source tree::

    pip install -e git+https://github.com/aldryn/aldryn-events.git#egg=aldryn-events

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
    'mptt',
    'parler',
    'sortedm2m',
    'standard_form',

listed in ``INSTALLED_APPS``, *after* ``'cms'``.

Now run ``python manage.py migrate`` to prepare the database for the new
application.

To install the addon on Aldryn, all you need to do is follow this
`installation link <https://control.aldryn.com/control/?select_project_for_addon=aldryn-events>`_
on the Aldryn Marketplace and follow the instructions.
