# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0013_remove_eventsconfig_show_ongoing_first'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventsconfigtranslation',
            options={'default_permissions': (), 'verbose_name': 'events config Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='eventtranslation',
            options={'default_permissions': (), 'verbose_name': 'Event Translation', 'managed': True},
        ),
        migrations.RemoveField(
            model_name='eventtranslation',
            name='flyer',
        ),
        migrations.AlterField(
            model_name='eventsconfigtranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventtranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
    ]
