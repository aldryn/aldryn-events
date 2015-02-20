# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from parler.utils.context import switch_language


def forwards(apps, schema_editor):
    Event = apps.get_model('aldryn_events', 'Event')
    for event in Event.objects.all():
        first = True
        for tr in event.translations.all():
            if first:
                event.description_new_id = tr.description_id
                event.save()
                first = False
            else:
                plugins = (
                    tr.description.cmsplugin_set.filter(language=tr.language_code)
                )
                plugins.update(placeholder_id=event.description_new_id)

def backwards(apps, schema_editor):
    Event = apps.get_model('aldryn_events', 'Event')
    for event in Event.objects.all():
        event.translations.update(description_id=event.description_new_id)


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0009_auto_add_field_event_description_new'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
