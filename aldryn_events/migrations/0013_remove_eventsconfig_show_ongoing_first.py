# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0012_eventsconfig_show_ongoing_first'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventsconfig',
            name='show_ongoing_first',
        ),
    ]
