# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file
import django.db.models.deletion
import djangocms_text_ckeditor.fields
from django.conf import settings
import django.utils.timezone
import cms.models.fields
import sortedm2m.fields
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=150, verbose_name='slug', blank=True)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('start_time', models.TimeField(null=True, verbose_name='start time', blank=True)),
                ('end_date', models.DateField(null=True, verbose_name='end date', blank=True)),
                ('end_time', models.TimeField(null=True, verbose_name='end time', blank=True)),
                ('is_published', models.BooleanField(default=True, help_text='wether the event should be displayed', verbose_name='is published')),
                ('publish_at', models.DateTimeField(default=django.utils.timezone.now, help_text='time at which the event should be published', verbose_name='publish at')),
                ('detail_link', models.URLField(default='', help_text='external link to details about this event', verbose_name='external link', blank=True)),
                ('register_link', models.URLField(default='', help_text='link to an external registration system', verbose_name='registration link', blank=True)),
                ('enable_registration', models.BooleanField(default=False, verbose_name='enable event registration')),
                ('registration_deadline_at', models.DateTimeField(default=None, null=True, verbose_name='allow registartion until', blank=True)),
                ('description', cms.models.fields.PlaceholderField(slotname='aldryn_events_event_description', editable=False, to='cms.Placeholder', null=True, verbose_name='description')),
            ],
            options={
                'ordering': ('start_date', 'start_time', 'end_date', 'end_time'),
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventCoordinator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, blank=True)),
                ('email', models.EmailField(max_length=80, blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, unique=True, verbose_name='user')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('style', models.CharField(default='standard', max_length=50, verbose_name='Style', choices=[('standard', 'Standard')])),
                ('events', sortedm2m.fields.SortedManyToManyField(help_text=None, to='aldryn_events.Event', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='EventTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='translated', max_length=150, verbose_name='title')),
                ('short_description', djangocms_text_ckeditor.fields.HTMLField(default='', help_text='translated', verbose_name='short description', blank=True)),
                ('location', models.TextField(default='', verbose_name='location', blank=True)),
                ('location_lat', models.FloatField(null=True, verbose_name='location latitude', blank=True)),
                ('location_lng', models.FloatField(null=True, verbose_name='location longitude', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_events.Event', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'aldryn_events_event_translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('language_code', models.CharField(default='en', max_length=32, choices=[('en', 'English')])),
                ('salutation', models.CharField(default='mrs', max_length=5, verbose_name='Anrede', choices=[('mrs', 'Frau'), ('mr', 'Herr')])),
                ('company', models.CharField(default='', max_length=100, verbose_name='Company', blank=True)),
                ('first_name', models.CharField(max_length=100, verbose_name='Vorname')),
                ('last_name', models.CharField(max_length=100, verbose_name='Nachname')),
                ('address', models.TextField(default='', verbose_name='Adresse', blank=True)),
                ('address_zip', models.CharField(max_length=4, verbose_name='PLZ')),
                ('address_city', models.CharField(max_length=100, verbose_name='Ort')),
                ('phone', models.CharField(default='', max_length=20, verbose_name='Phone number', blank=True)),
                ('mobile', models.CharField(default='', max_length=20, verbose_name='Mobile number', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='E-Mail')),
                ('message', models.TextField(default='', verbose_name='Message', blank=True)),
                ('event', models.ForeignKey(to='aldryn_events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UpcomingPluginItem',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('past_events', models.BooleanField(default=False, verbose_name='selection', choices=[(False, 'future events'), (True, 'past events')])),
                ('style', models.CharField(default='standard', max_length=50, verbose_name='Style', choices=[('standard', 'Standard')])),
                ('latest_entries', models.PositiveSmallIntegerField(default=5, help_text='The number of latests events to be displayed.', verbose_name='latest entries')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterUniqueTogether(
            name='eventtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='event',
            name='event_coordinators',
            field=models.ManyToManyField(to='aldryn_events.EventCoordinator', null=True, verbose_name='event coordinators', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='flyer',
            field=filer.fields.file.FilerFileField(related_name='event_flyers', on_delete=django.db.models.deletion.SET_NULL, verbose_name='flyer', blank=True, to='filer.File', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=filer.fields.image.FilerImageField(related_name='event_images', on_delete=django.db.models.deletion.SET_NULL, verbose_name='image', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
    ]
