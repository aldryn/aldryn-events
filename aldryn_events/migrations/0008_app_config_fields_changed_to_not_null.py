# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0007_set_default_namespaces'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventcalendarplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventlistplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='upcomingpluginitem',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig'),
            preserve_default=True,
        ),
    ]
