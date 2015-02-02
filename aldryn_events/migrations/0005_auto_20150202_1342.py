# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0004_auto_20150128_1846'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventtranslation',
            options={'default_permissions': (), 'verbose_name': 'Event Translation', 'managed': True},
        ),
        migrations.AlterField(
            model_name='registration',
            name='address_zip',
            field=models.CharField(max_length=20, verbose_name='ZIP CODE'),
            preserve_default=True,
        ),
    ]
