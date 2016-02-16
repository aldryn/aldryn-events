# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from aldryn_apphooks_config.models import AppHookConfig
from aldryn_reversion.core import version_controlled_content
from cms.models.fields import PlaceholderField
from parler.models import TranslatableModel, TranslatedFields


@python_2_unicode_compatible
@version_controlled_content
class EventsConfig(TranslatableModel, AppHookConfig):
    """Adds some translatable, per-app-instance fields."""
    translations = TranslatedFields(
        app_title=models.CharField(
            _('application title'), max_length=234, default=''))

    latest_first = models.BooleanField(
        _('Show latest events first?'), default=False,
        help_text=_('(Changes here may require a restart.)'))

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

    def __str__(self):
        # use app_title if it was provided, otherwise use namespace
        title = getattr(self, 'app_title', self.namespace)
        if self.cmsapp:
            return '{0} / {1}'.format(self.cmsapp.name, title)
        else:
            return '{0} / {1}'.format(self.type, title)
