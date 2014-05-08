# -*- coding: utf-8 -*-
import datetime
from django.core.urlresolvers import reverse
from django import forms
from django.http import Http404
from django.utils import translation
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
)
from django.utils.translation import ugettext as _
from aldryn_events import request_events_event_identifier
from django.utils.dates import MONTHS

from .utils import (
    build_events_by_year,
    send_user_confirmation_email,
    send_manager_confirmation_email,
    build_calendar,
)
from .models import Event, Registration
from .forms import EventRegistrationForm
from .conf import settings


class NavigationMixin(object):
    def get_context_data(self, **kwargs):
        context = super(NavigationMixin, self).get_context_data(**kwargs)
        events_by_year = build_events_by_year(
            events=Event.objects.future()
        )
        context['events_by_year'] = events_by_year
        archived_events_by_year = build_events_by_year(
            events=Event.objects.archive(),
            is_archive_view=True,
        )
        context['archived_events_by_year'] = archived_events_by_year
        context['event_year'] = self.kwargs.get('year')
        context['event_month'] = self.kwargs.get('month')
        context['event_day'] = self.kwargs.get('day')
        return context


class EventListView(NavigationMixin, ListView):
    model = Event
    template_name = 'aldryn_events/events_list.html'
    archive = False

    def get_queryset(self):
        if self.archive:
            qs = self.model.objects.archive()
        else:
            qs = self.model.objects.future()
        year = self.kwargs.get('year', None)
        month = self.kwargs.get('month', None)
        day = self.kwargs.get('day', None)
        if year:
            qs = qs.filter(start_at__year=year)
        if month:
            qs = qs.filter(start_at__month=month)
        if day:
            qs = qs.filter(start_at__day=day)
        qs = qs.order_by('start_at', 'end_at')
        return qs


class EventDetailView(NavigationMixin, CreateView):
    model = Registration
    template_name = 'aldryn_events/events_detail.html'
    form_class = EventRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.published().get(slug=kwargs['slug'])
        except Event.DoesNotExist:
            raise Http404
        setattr(self.request, request_events_event_identifier, self.event)
        if hasattr(request, 'toolbar'):
            request.toolbar.set_object(self.event)
        return super(EventDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['already_registered'] = self.event.id in self.request.session.get('registered_events', set())
        return context

    def form_valid(self, form):
        r = super(EventDetailView, self).form_valid(form)
        registered_events = set(self.request.session.get('registered_events', set()))
        registered_events.add(self.event.id)
        self.request.session['registered_events'] = registered_events
        if settings.ALDRYN_EVENTS_USER_REGISTRATION_EMAIL:
            send_user_confirmation_email(form.instance, form.language_code)
        coordinator_emails = list(self.event.event_coordinators.all().values_list('email', flat=True))
        coordinator_emails.extend([a[1] for a in settings.ALDRYN_EVENTS_MANAGERS])
        if coordinator_emails:
            send_manager_confirmation_email(form.instance, form.language_code, coordinator_emails)
        return r

    def get_success_url(self):
        return reverse('events_detail', kwargs={'slug': self.kwargs['slug']})

    def get_form_kwargs(self):
        kwargs = super(EventDetailView, self).get_form_kwargs()
        kwargs['event'] = self.event
        kwargs['language_code'] = translation.get_language()
        return kwargs


class ResetEventRegistration(FormView):
    form_class = forms.Form

    def dispatch(self, request, *args, **kwargs):
        self.event = Event.objects.get(slug=kwargs['slug'])
        return super(ResetEventRegistration, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        registered_events = self.request.session.get('registered_events', set())
        registered_events.remove(self.event.id)
        self.request.session['registered_events'] = registered_events
        return super(ResetEventRegistration, self).form_valid(form)

    def get_success_url(self):
        return reverse('events_detail', kwargs={'slug':self.event.slug})


class EventDatesView(TemplateView):
    template_name = 'aldryn_events/includes/calendar_dates.html'

    def get_context_data(self, **kwargs):
        ctx = super(EventDatesView, self).get_context_data(**kwargs)
        if not 'year' in ctx or not 'month' in ctx:
            today = datetime.datetime.today()
            ctx['month'] = today.month
            ctx['year'] = today.year

        current_date = datetime.date(day=1, month=int(ctx['month']), year=int(ctx['year']))
        ctx['days'] = build_calendar(ctx['year'], ctx['month'])
        ctx['current_date'] = current_date
        ctx['last_month'] = current_date + datetime.timedelta(days=-1)
        ctx['next_month'] = current_date + datetime.timedelta(days=35)
        return ctx
