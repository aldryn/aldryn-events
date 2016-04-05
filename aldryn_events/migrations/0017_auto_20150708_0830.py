# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0016_auto_20150706_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='language_code',
            field=models.CharField(default='en', max_length=32, choices=[('en', 'English'), ('de', 'German')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='salutation',
            field=models.CharField(default='mrs', max_length=5, verbose_name='Salutation', choices=[('mrs', 'Ms.'), ('mr', 'Mr.')]),
            preserve_default=True,
        ),
    ]
