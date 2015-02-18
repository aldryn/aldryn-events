# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards(apps, schema_editor):
    for entry in apps.get_model('aldryn_events', 'Event').objects.all():
        entry.description_new = entry.description
        entry.save()

def backwards(apps, schema_editor):
    for entry in apps.get_model('aldryn_events', 'Event').objects.all():
        entry.description = entry.description_new
        entry.save()



class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0009_auto_add_field_event_description_new'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
