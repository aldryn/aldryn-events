# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0010_data_migrate_description_out_of_translations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='description_new',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='eventtranslation',
            name='description',
        ),
    ]
