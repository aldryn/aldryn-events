# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('aldryn_events', '0014_auto_20150324_0443'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_detail_bottom',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_detail_bottom', slotname='events_detail_bottom', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_detail_footer',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_detail_footer', slotname='events_detail_footer', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_detail_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_detail_top', slotname='events_detail_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_list_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_list_top', slotname='events_list_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_list_top_ongoing',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_list_top_ongoing', slotname='events_list_top_ongoing', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_registration',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_registration', slotname='events_registration', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_registration_footer',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_registration_footer', slotname='events_registration_footer', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_sidebar',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_sidebar', slotname='events_sidebar', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventsconfig',
            name='placeholder_events_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_events_top', slotname='events_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventsconfig',
            name='namespace',
            field=models.CharField(default=None, unique=True, max_length=100, verbose_name='instance namespace'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='language_code',
            field=models.CharField(default='en', max_length=32, choices=[('en', 'English'), ('de', 'Deutsch')]),
            preserve_default=True,
        ),
    ]
