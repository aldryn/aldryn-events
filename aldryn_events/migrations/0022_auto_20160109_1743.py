# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0021_eventcoordinator_fk_to_one_to_one'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='E-Mail'),
        ),
    ]
