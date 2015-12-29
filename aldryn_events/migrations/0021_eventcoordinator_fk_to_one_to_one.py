# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_events', '0020_m2m_remove_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventcoordinator',
            name='user',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
