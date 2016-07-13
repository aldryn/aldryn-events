# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction
from django.conf import settings
from django.db.utils import ProgrammingError, OperationalError


def create_default_namespaces(apps, schema_editor):
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    models_to_fetch = [
        apps.get_model('aldryn_events', 'Event'),
        apps.get_model('aldryn_events', 'UpcomingPluginItem'),
        apps.get_model('aldryn_events', 'EventListPlugin'),
        apps.get_model('aldryn_events', 'EventCalendarPlugin'),
    ]

    app_config, created = EventsConfig.objects.get_or_create(
        namespace='aldryn_events')

    if created:
        app_config_translation = app_config.translations.create()
        app_config_translation.language_code = settings.LANGUAGES[0][0]
        app_config_translation.app_title = 'Events'
        app_config_translation.save()

    for model in models_to_fetch:
        # if cms migrations migrated to latest and after that we will try to
        # migrate this - we would get an exception because apps.get_model
        # contains cms models at point of dependency migration
        # so if that is the case - import real model.
        if not model.objects.filter(app_config__isnull=True).exists():
            # If there are no object yet, of this type, do nothing.
            continue

        with transaction.atomic():
            model_objects = list(model.objects.filter(
                app_config__isnull=True))

        for entry in model_objects:
            entry.app_config = app_config
            entry.save()


def remove_namespaces(apps, schema_editor):
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    EventsConfig.objects.filter(namespace='aldryn_events').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('aldryn_events', '0006_add_app_config_to_events_and_plugins'),
    ]

    operations = [
        migrations.RunPython(create_default_namespaces, remove_namespaces),
    ]
