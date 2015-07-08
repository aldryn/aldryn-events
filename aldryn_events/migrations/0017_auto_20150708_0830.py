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
            field=models.CharField(default=b'en', max_length=32, choices=[(b'en', b'English'), (b'de', b'German')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='salutation',
            field=models.CharField(default=b'mrs', max_length=5, verbose_name='Salutation', choices=[(b'mrs', 'Ms.'), (b'mr', 'Mr.')]),
            preserve_default=True,
        ),
    ]
