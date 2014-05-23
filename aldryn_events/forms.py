# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template import TemplateDoesNotExist
from django.template.loader import select_template

from .utils import send_user_confirmation_email, send_manager_confirmation_email

from .models import Registration, UpcomingPluginItem


class EventRegistrationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.language_code = kwargs.pop('language_code')
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget = forms.Textarea(attrs={'rows': 2})

    def clean(self):
        if self.event.is_registration_deadline_passed:
            raise ValidationError(_('the registration deadline for this event has already passed'))
        return self.cleaned_data

    def send_user_notification(self):
        if settings.ALDRYN_EVENTS_USER_REGISTRATION_EMAIL:
            send_user_confirmation_email(self.instance, self.language_code)

    def send_admin_notification(self):
        coordinators = self.event.event_coordinators.select_related('user')
        coordinator_emails = [coordinator.email_address for coordinator in coordinators]
        coordinator_emails.extend([a[1] for a in settings.ALDRYN_EVENTS_MANAGERS])

        if coordinator_emails:
            send_manager_confirmation_email(self.instance, self.language_code, coordinator_emails)

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


class UpcomingPluginForm(forms.ModelForm):
    model = UpcomingPluginItem

    def clean_style(self):
        style = self.cleaned_data.get('style')
        # Check if template for style exists:
        try:
            select_template(['aldryn_events/plugins/upcoming/%s/upcoming.html' % style])
        except TemplateDoesNotExist:
            raise forms.ValidationError("Not a valid style (Template does not exist)")
        return style
