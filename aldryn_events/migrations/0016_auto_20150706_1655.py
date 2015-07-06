# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction
from django.db.models import get_model
from django.db.utils import ProgrammingError
from cms.models.fields import PlaceholderField


def create_missing_placeholders(apps, schema_editor):
    print 'data migration'
    EventsConfig = apps.get_model('aldryn_events', 'EventsConfig')
    Placeholder = apps.get_model('cms', 'Placeholder')
    configs_qs = EventsConfig.objects.all()

    try:
        # to avoid the following error:
        #   django.db.utils.InternalError: current transaction is aborted,
        #   commands ignored until end of transaction block
        # we need to cleanup or avoid that by making them atomic.
        with transaction.atomic():
            configs = list(configs_qs)
    except ProgrammingError:
        print 'exception'
        # most likely we also need the latest Placeholder model
        from cms.models import Placeholder
        NewEventsConfig = get_model('aldryn_events.{0}'.format(EventsConfig.__name__))
        with transaction.atomic():
            configs = NewEventsConfig.objects.filter()

    # get placeholders and their names
    print configs
    for cfg in configs:
        for field in cfg._meta.fields:
            if not field.__class__ == PlaceholderField:
                # skip other fields.
                continue
            placeholder_name = field.name
            placeholder_id_name = '{0}_id'.format(placeholder_name)
            placeholder_id = getattr(cfg, placeholder_id_name)
            if placeholder_id is not None:
                # do not process if it has a reference to placeholder field.
                continue
            # since there is no placeholder - create it, we cannot use
            # get_or_create because it can get placeholder from other config
            PlaceholderField.pre_save(PlaceholderField(slotname=placeholder_name), cfg, False)
            # new_placeholder = Placeholder.objects.create(slot=placeholder_name)
            # setattr(cfg, placeholder_name, PlaceholderField(slotname=placeholder_name))
            # print new_placeholder.id
            # after we process all placeholder fields - save config,
            # so that django can pick up them.
            # IMPORTANT: Please don't move it outside of a loop, this would
            # break this migration.
            # cfg.save()
    print 'data migration end'


def noop_backwards(apps, schema_editor):
    # doesn't make sense to do something here
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('aldryn_events', '0015_auto_20150702_1220'),
    ]

    operations = [
        migrations.RunPython(create_missing_placeholders, noop_backwards)
    ]
