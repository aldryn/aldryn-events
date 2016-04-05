# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file
import filer.fields.image
import django.db.models.deletion
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('filer', '__first__'),
        ('aldryn_events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventtranslation',
            options={'default_permissions': (), 'verbose_name': 'Event Translation'},
        ),
        migrations.AddField(
            model_name='eventtranslation',
            name='description_new',
            field=cms.models.fields.PlaceholderField(slotname='aldryn_events_event_description', editable=False, to='cms.Placeholder', null=True, verbose_name='description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventtranslation',
            name='flyer_new',
            field=filer.fields.file.FilerFileField(related_name='event_flyers', on_delete=django.db.models.deletion.SET_NULL, verbose_name='flyer', blank=True, to='filer.File', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventtranslation',
            name='image_new',
            field=filer.fields.image.FilerImageField(related_name='event_images', on_delete=django.db.models.deletion.SET_NULL, verbose_name='image', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventtranslation',
            name='slug_new',
            field=models.SlugField(max_length=150, verbose_name='slug', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='flyer',
            field=filer.fields.file.FilerFileField(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='flyer', blank=True, to='filer.File', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=filer.fields.image.FilerImageField(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='image', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='registration_deadline_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='allow registration until', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(max_length=150, verbose_name='slug', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventtranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[('en', 'en'), ('de', 'de')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='address',
            field=models.TextField(default='', verbose_name='Address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='address_city',
            field=models.CharField(max_length=100, verbose_name='City'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='address_zip',
            field=models.CharField(max_length=4, verbose_name='ZIP CODE'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='First name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='language_code',
            field=models.CharField(default='en', max_length=32, choices=[('en', 'en'), ('de', 'de')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='Last name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='salutation',
            field=models.CharField(default='mrs', max_length=5, verbose_name='Salutation', choices=[('mrs', 'Frau'), ('mr', 'Herr')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
