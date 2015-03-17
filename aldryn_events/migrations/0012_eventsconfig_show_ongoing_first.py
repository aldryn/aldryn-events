# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0011_auto_rename_event_description_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsconfig',
            name='show_ongoing_first',
            field=models.BooleanField(default=False, help_text="When flagged will add an ongoing_objects to the context and exclude these objects from the normal list. If you are using the default template it's rendered as 'Current events'. Note: ongoing objects are not paginated.", verbose_name='Show ongoing events first on events page'),
            preserve_default=True,
        ),
    ]
