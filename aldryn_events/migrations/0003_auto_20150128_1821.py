# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations


def forwards_func(apps, schema_editor):
    Event = apps.get_model('aldryn_events', 'Event')

    for obj in Event.objects.all():

        # Set all translations with current values for new translated fields because each translation
        # have used same value before this migration.
        for tobj in obj.translations.all():
            tobj.slug_new = obj.slug
            tobj.description_new = obj.description
            tobj.image_new = obj.image
            tobj.flyer_new = obj.flyer
            tobj.save()


def backwards_func(apps, schema_editor):
    Event = apps.get_model('aldryn_events', 'Event')
    EventTranslation = apps.get_model('aldryn_events', 'EventTranslation')

    for obj in Event.objects.all():
        translations = EventTranslation.objects.filter(master_id=obj.pk)

        # Set translated fields to old untranslated fields. Use default translation to do it is our
        # best shot because default language probably is same.
        translation = _get_default_translation(translations)
        obj.slug = translation.slug_new
        obj.description = translation.description_new
        obj.image = translation.image_new
        obj.flyer = translation.flyer_new
        obj.save()

        for tr in translations.exclude(pk=translation.pk):
            plugins = tr.description_new.cmsplugin_set.filter(language=tr.language_code)
            for plugin in plugins:
                plugin.placeholder_id = obj.description_id
                plugin.save()


def _get_default_translation(translations):
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0002_auto_20150128_1821'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
