# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0017_auto_20150708_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsconfig',
            name='latest_first',
            field=models.BooleanField(default=False, verbose_name='Show latest events first?'),
            preserve_default=True,
        ),
    ]
