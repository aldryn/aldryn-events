# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0003_auto_20150128_1821'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventtranslation',
            old_name='description_new',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='eventtranslation',
            old_name='flyer_new',
            new_name='flyer',
        ),
        migrations.RenameField(
            model_name='eventtranslation',
            old_name='image_new',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='eventtranslation',
            old_name='slug_new',
            new_name='slug',
        ),
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.RemoveField(
            model_name='event',
            name='flyer',
        ),
        migrations.RemoveField(
            model_name='event',
            name='image',
        ),
        migrations.RemoveField(
            model_name='event',
            name='slug',
        ),
        migrations.AlterUniqueTogether(
            name='eventtranslation',
            unique_together=set([('language_code', 'master'), ('language_code', 'slug')]),
        ),
    ]
