# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app_data.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('aldryn_events', '0005_auto_20150202_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCalendarPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='EventsConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('namespace', models.CharField(default=None, max_length=100, verbose_name='instance namespace')),
                ('app_data', app_data.fields.AppDataField(default='{}', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventsConfigTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[('en', 'en'), ('de', 'de')])),
                ('app_title', models.CharField(max_length=234, verbose_name='application title')),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_events.EventsConfig', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'aldryn_events_eventsconfig_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'events config Translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='eventsconfigtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='eventcalendarplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlistplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='upcomingpluginitem',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_events.EventsConfig', null=True),
            preserve_default=True,
        ),
    ]
