# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_default_namespaces(apps, schema_editor):
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    Event = apps.get_model('aldryn_events', 'Event')
    UpcomingPluginItem = apps.get_model('aldryn_events', 'UpcomingPluginItem')
    EventListPlugin = apps.get_model('aldryn_events', 'EventListPlugin')
    EventCalendarPlugin = apps.get_model('aldryn_events', 'EventCalendarPlugin')

    ns, created = EventsConfig.objects.get_or_create(namespace='aldryn_events')

    for model in [Event, EventListPlugin, UpcomingPluginItem, EventCalendarPlugin]:
        for entry in model.objects.filter(app_config__isnull=True):
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
