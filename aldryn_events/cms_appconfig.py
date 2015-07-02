# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.models import AppHookConfig
from cms.models.fields import PlaceholderField
from parler.models import TranslatableModel, TranslatedFields


class EventsConfig(TranslatableModel, AppHookConfig):
    """Adds some translatable, per-app-instance fields."""
    translations = TranslatedFields(
        app_title=models.CharField(_('application title'), max_length=234),
    )

    # Category List PHFs
    placeholder_events_top = PlaceholderField(
        'events_top', related_name='aldryn_events_top')

    placeholder_events_sidebar = PlaceholderField(
        'events_sidebar', related_name='aldryn_events_sidebar')

    placeholder_events_list_top_ongoing = PlaceholderField(
        'events_list_top_ongoing',
        related_name='aldryn_events_list_top_ongoing')

    # Question list PHFs
    placeholder_events_list_top = PlaceholderField(
        'events_list_top', related_name='aldryn_events_list_top')

    placeholder_events_detail_top = PlaceholderField(
        'events_detail_top', related_name='aldryn_events_detail_top')

    placeholder_events_detail_bottom = PlaceholderField(
        'events_detail_bottom', related_name='aldryn_events_detail_bottom')

    placeholder_events_detail_footer = PlaceholderField(
        'events_detail_footer', related_name='aldryn_events_detail_footer')

    placeholder_events_registration = PlaceholderField(
        'events_registration', related_name='aldryn_events_registration')

    placeholder_events_registration_footer = PlaceholderField(
        'events_registration_footer',
        related_name='aldryn_events_registration_footer')
