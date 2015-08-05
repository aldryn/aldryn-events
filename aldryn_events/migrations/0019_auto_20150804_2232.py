# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0018_eventsconfig_newest_first'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsconfig',
            name='latest_first',
            field=models.BooleanField(default=False, help_text='(Changes here may require a restart.)', verbose_name='Show latest events first?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventsconfigtranslation',
            name='app_title',
            field=models.CharField(default='', max_length=234, verbose_name='application title', blank=True),
            preserve_default=True,
        ),
    ]
