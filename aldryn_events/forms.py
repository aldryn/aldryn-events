# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.exceptions import ValidationError
from django.forms import DateTimeField, TimeField, DateField
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils import timezone
from django.utils.html import format_html
from django.template import TemplateDoesNotExist
from django.template.loader import select_template

from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from parler.forms import TranslatableModelForm
from cms.models import Page

from .models import (
    Registration, UpcomingPluginItem, Event, EventsConfig,
    EventListPlugin, EventCalendarPlugin,
)
from .utils import (
    send_user_confirmation_email, send_manager_confirmation_email,
    is_valid_namespace,
)


class CustomAdminSplitDateTime(AdminSplitDateTime):
    def format_output(self, rendered_widgets):
        return format_html(
            '<div class="field-box">{0} {1}</div>'
            '<div class="field-box">{2} {3}</div>',
            ugettext('Date:'), rendered_widgets[0],
            ugettext('Time:'), rendered_widgets[1],
        )


class EventAdminForm(TranslatableModelForm):

    class Meta:
        model = Event
        # since form is intended to be only for internal use we can allow all
        # fields
        fields = '__all__'
        widgets = {
            'registration_deadline_at': CustomAdminSplitDateTime,
            'publish_at': CustomAdminSplitDateTime,
        }

    def __init__(self, *args, **kwargs):
        super(EventAdminForm, self).__init__(*args, **kwargs)
        now = timezone.now()
        help_text = _('Acceptable Formats: %(format_list)s')

        for key, field in self.fields.items():
            if (isinstance(field, DateField) or isinstance(field, TimeField) or
                    isinstance(field, DateTimeField)):
                format_list = ', '.join(
                    [now.strftime(f) for f in field.input_formats]
                )
                self.fields[key].help_text = (
                    help_text % ({'format_list': format_list})
                )
        # FIXME: add a notification if user selects not apphooked Events config
        if 'app_config' in self.fields:
            # if has only one choice, select it by default
            if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None


class EventRegistrationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.language_code = kwargs.pop('language_code')
        super(EventRegistrationForm, self).__init__(*args, **kwargs)

        if 'address' in self.fields:
            self.fields['address'].widget = forms.Textarea(attrs={'rows': 1})

        if 'message' in self.fields:
            self.fields['message'].widget = forms.Textarea(attrs={'rows': 5})

    def clean(self):
        if self.event.is_registration_deadline_passed:
            raise ValidationError(
                _('the registration deadline for this event has already '
                  'passed')
            )
        return self.cleaned_data

    def send_user_notification(self):
        if settings.ALDRYN_EVENTS_USER_REGISTRATION_EMAIL:
            send_user_confirmation_email(self.instance, self.language_code)

    def send_admin_notification(self):
        coordinators = self.event.event_coordinators.select_related('user')
        coordinator_emails = (
            [coordinator.email_address for coordinator in coordinators]
        )
        coordinator_emails.extend(
            [a[1] for a in settings.ALDRYN_EVENTS_MANAGERS]
        )

        if coordinator_emails:
            send_manager_confirmation_email(
                self.instance, self.language_code, coordinator_emails
            )

    def save(self, commit=True):
        registration = super(EventRegistrationForm, self).save(commit=False)
        registration.event = self.event
        registration.language_code = self.language_code

        if commit:
            registration.save()

        self.send_user_notification()
        self.send_admin_notification()

        return registration

    class Meta:
        model = Registration
        fields = (
            'salutation',
            'company',
            'first_name',
            'last_name',
            'address',
            'address_zip',
            'address_city',
            'phone',
            'mobile',
            'email',
            'message'
        )


class AppConfigPluginFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(AppConfigPluginFormMixin, self).__init__(*args, **kwargs)
        # get available event configs, that have the same namespace
        # as pages with namespaces. that will ensure that user wont
        # select config that is not app hooked because that
        # will lead to a 500 error until that config wont be used.
        available_configs = EventsConfig.objects.filter(
            namespace__in=Page.objects.exclude(
                application_namespace__isnull=True).values_list(
                'application_namespace', flat=True))

        published_configs_pks = [
            config.pk for config in available_configs
            if is_valid_namespace(config.namespace)]

        self.fields['app_config'].queryset = available_configs.filter(
            pk__in=published_configs_pks)
        # inform user that there are not published namespaces
        # which he shouldn't use
        not_published = available_configs.exclude(
            pk__in=published_configs_pks).values_list(
            'namespace', flat=True)
        msg = ugettext(
            'Following app_configs is app hooked but pages are not '
            'published, to use them - publish pages to which they are '
            'attached.')
        not_published_namespaces = '; '.join(not_published)
        full_message = '{0} \n<br/>{1}'.format(msg, not_published_namespaces)
        # update help text
        if (not self.fields['app_config'].help_text or
                len(self.fields['app_config'].help_text.strip()) < 1):
            self.fields['app_config'].help_text = full_message
        else:
            self.fields['app_config'].help_text += full_message

        # pre select app config if there is only one option
        if self.fields['app_config'].queryset.count() == 1:
            self.fields['app_config'].empty_label = None

    def clean(self):
        # since namespace is not a unique thing we need to validate it
        # additionally because it is possible that there is a page with same
        # namespace as a events config but which is using other app_config,
        # which also would lead to same 500 error. The easiest way is to try
        # to reverse, in case of success that would mean that the app_config
        # is correct and can be used.
        data = super(AppConfigPluginFormMixin, self).clean()
        app_config = data.get('app_config', None)
        namespace = getattr(app_config, 'namespace', None)

        if namespace and not is_valid_namespace(namespace):
            raise ValidationError(
                _('Seems that selected Event config is not plugged to any '
                  'page, or maybe that page is not published.'
                  'Please select Event config that is being used.'),
                code='invalid')
        return data


class UpcomingPluginForm(AppConfigPluginFormMixin, forms.ModelForm):

    class Meta:
        model = UpcomingPluginItem
        fields = ['app_config', 'past_events', 'latest_entries', 'style',
                  'cache_duration']

    def clean_style(self):
        style = self.cleaned_data.get('style')
        # Check if template for style exists:
        try:
            select_template(
                ['aldryn_events/plugins/upcoming/%s/upcoming.html' % style]
            )
        except TemplateDoesNotExist:
            raise forms.ValidationError(
                "Not a valid style (Template does not exist)"
            )
        return style


class EventListPluginForm(AppConfigPluginFormMixin, forms.ModelForm):
    model = EventListPlugin

    def clean(self):
        data = super(EventListPluginForm, self).clean()
        # save only events for selected app_config
        selected_events = data.get('events', [])
        app_config = data['app_config']
        new_events = [event for event in selected_events
                      if event.app_config.pk == app_config.pk]
        data['events'] = new_events
        return data


class EventCalendarPluginForm(AppConfigPluginFormMixin, forms.ModelForm):
    model = EventCalendarPlugin


class EventOptionForm(AppDataForm):
    show_ongoing_first = forms.BooleanField(
        required=False,
        help_text=_(
            "When flagged will add an ongoing_objects to the context and "
            "exclude these objects from the normal list. If you are using "
            "the default template it's rendered as 'Current events'. Note: "
            "ongoing objects are not paginated."
        )
    )

setup_config(EventOptionForm, EventsConfig)
