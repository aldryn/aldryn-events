# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0024_auto_20160623_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventcalendarplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_events_eventcalendarplugin', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='eventlistplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_events_eventlistplugin', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='upcomingpluginitem',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_events_upcomingpluginitem', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
    ]
