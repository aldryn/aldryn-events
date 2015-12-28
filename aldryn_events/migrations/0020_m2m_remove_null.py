# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0019_auto_20150804_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_coordinators',
            field=models.ManyToManyField(to='aldryn_events.EventCoordinator', verbose_name='event coordinators', blank=True),
        ),
        migrations.AlterField(
            model_name='eventlistplugin',
            name='events',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='aldryn_events.Event', blank=True),
        ),
    ]
