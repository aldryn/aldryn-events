# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.db import transaction
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.api import add_plugin
from cms.utils import permissions
from cms.utils.conf import get_cms_setting
from cms.wizards.wizard_pool import wizard_pool
from cms.wizards.wizard_base import Wizard
from cms.wizards.forms import BaseFormMixin

from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.html import clean_html
from parler.forms import TranslatableModelForm
from reversion.revisions import revision_context_manager

from .cms_appconfig import EventsConfig
from .models import Event
from .utils import is_valid_namespace


class EventWizard(Wizard):

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add an Event.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        # No one can create an Event, if there is no app_config yet.
        configs = EventsConfig.objects.all()
        if not configs or not any([is_valid_namespace(config.namespace)
                                   for config in configs]):
            return False
        # Ensure user has permission to create event.
        if user.is_superuser or user.has_perm('aldryn_events.add_event'):
            return True

        # By default, no permission.
        return False


class CreateEventForm(BaseFormMixin, TranslatableModelForm):
    """
    The ModelForm for the Event wizard. Note that Event has few
    translated fields that we need to access, so, we use TranslatableModelForm
    """

    description = forms.CharField(
        label="description", required=False, widget=TextEditorWidget,
        help_text=_("Optional. If provided, will be added to the main body of "
                    "the Event.")
    )

    class Meta:
        model = Event
        fields = ['title', 'slug', 'short_description', 'location',
                  'app_config', 'is_published', 'start_date', 'end_date',
                  'description']

    def __init__(self, **kwargs):
        super(CreateEventForm, self).__init__(**kwargs)
        # If there's only 1 app_config, don't bother show the
        # app_config choice field, we'll choose the option for the user.
        app_configs = EventsConfig.objects.all()
        # check if app config is apphooked
        app_configs = [app_config
                       for app_config in app_configs
                       if is_valid_namespace(app_config.namespace)]
        if len(app_configs) == 1:
            self.fields['app_config'].widget = forms.HiddenInput()
            self.fields['app_config'].initial = app_configs[0].pk
        self.fields['start_date'].help_text = _(
            'Date Acceptable Formats: 2015-11-30, 11/30/2015, 11/30/15'
        )
        self.fields['end_date'].help_text = _(
            'Date Acceptable Formats: 2015-11-30, 11/30/2015, 11/30/15'
        )

    def save(self, commit=True):
        event = super(CreateEventForm, self).save(commit=False)

        if not commit:
            return event

        # If 'content' field has value, create a TextPlugin with same and add
        # it to the PlaceholderField
        description = clean_html(
            self.cleaned_data.get('description', ''), False)
        content_plugin = get_cms_setting('WIZARD_CONTENT_PLUGIN')
        if description and permissions.has_plugin_permission(
                self.user, content_plugin, 'add'):
            # If the event has not been saved, then there will be no
            # Placeholder set-up for this event yet, so, ensure we have saved
            # first.
            if not event.pk:
                event.save()

            if event and event.description:
                # we have to use kwargs because we don't know in advance what
                # is the 'body' field for configured plugin
                plugin_kwargs = {
                    'placeholder': event.description,
                    'plugin_type': content_plugin,
                    'language': self.language_code,
                    get_cms_setting('WIZARD_CONTENT_PLUGIN_BODY'): description,
                }
                add_plugin(**plugin_kwargs)

        with transaction.atomic():
            with revision_context_manager.create_revision():
                event.save()

                if self.user:
                    revision_context_manager.set_user(self.user)
                revision_context_manager.set_comment(
                    ugettext("Initial version."))
        return event

event_wizard = EventWizard(
    title=_(u"New Event"),
    weight=500,
    form=CreateEventForm,
    description=_(u"Create a new Event.")
)

wizard_pool.register(event_wizard)
