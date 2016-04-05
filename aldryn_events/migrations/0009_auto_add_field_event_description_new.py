# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0008_app_config_fields_changed_to_not_null'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventsconfigtranslation',
            options={'default_permissions': (), 'verbose_name': 'events config Translation'},
        ),
        migrations.AlterModelOptions(
            name='eventtranslation',
            options={'default_permissions': (), 'verbose_name': 'Event Translation'},
        ),
        migrations.AddField(
            model_name='event',
            name='description_new',
            field=cms.models.fields.PlaceholderField(slotname='aldryn_events_event_description', editable=False, to='cms.Placeholder', null=True, verbose_name='description'),
            preserve_default=True,
        ),
    ]
