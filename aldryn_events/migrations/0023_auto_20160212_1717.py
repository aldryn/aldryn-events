# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0022_auto_20160109_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsconfigtranslation',
            name='app_title',
            field=models.CharField(default='', max_length=234, verbose_name='application title'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='language_code',
            field=models.CharField(default='en', max_length=32, choices=[('en', 'English')]),
        ),
    ]
