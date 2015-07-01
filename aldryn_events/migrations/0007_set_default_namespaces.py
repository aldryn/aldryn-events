# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction
from django.db.models import get_model
from django.db.utils import ProgrammingError


def create_default_namespaces(apps, schema_editor):
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    models_to_fetch = [
        apps.get_model('aldryn_events', 'Event'),
        apps.get_model('aldryn_events', 'UpcomingPluginItem'),
        apps.get_model('aldryn_events', 'EventListPlugin'),
        apps.get_model('aldryn_events', 'EventCalendarPlugin'),
    ]

    ns, created = EventsConfig.objects.get_or_create(namespace='aldryn_events')

    for model in models_to_fetch:
        # if cms migrations migrated to latest and after that we will try to
        # migrate this - we would get an exception because apps.get_model
        # contains cms models at point of dependency migration
        # so if that is the case - import latest model.
        try:
            # to avoid the following error:
            #   django.db.utils.InternalError: current transaction is aborted,
            #   commands ignored until end of transaction block
            # we need to cleanup or avoid that by making them atomic.
            with transaction.atomic():
                model_objects = list(model.objects.filter(
                    app_config__isnull=True))
        except ProgrammingError:
            new_model = get_model('aldryn_events.{0}'.format(model.__name__))
            with transaction.atomic():
                model_objects = new_model.objects.filter(
                    app_config__isnull=True)
        for entry in model_objects:
            entry.app_config = ns
            entry.save()


def remove_namespaces(apps, schema_editor):
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    EventsConfig.objects.filter(namespace='aldryn_events').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0006_add_app_config_to_events_and_plugins'),
    ]

    operations = [
        migrations.RunPython(create_default_namespaces, remove_namespaces),
    ]
