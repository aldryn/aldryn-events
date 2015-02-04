# -*- coding: utf-8 -*-
import datetime
from aldryn_apphooks_config.utils import get_app_instance

from django.core.urlresolvers import reverse
from django import forms
from django.utils.translation import get_language_from_request
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
)

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_events import request_events_event_identifier

from .utils import (
    build_events_by_year,
    build_calendar,
)
from .models import Event, Registration
from .forms import EventRegistrationForm


class NavigationMixin(object):

    def get_context_data(self, **kwargs):
        context = super(NavigationMixin, self).get_context_data(**kwargs)
        language = get_language_from_request(self.request, check_path=True)
        events_by_year = build_events_by_year(
            events=Event.objects.namespace(self.namespace)
                                .future()
                                .translated(language).language(language)
        )
        context['events_by_year'] = events_by_year
        archived_events_by_year = build_events_by_year(
            events=Event.objects.namespace(self.namespace)
                                .archive()
                                .translated(language).language(language),
            is_archive_view=True,
        )
        context['archived_events_by_year'] = archived_events_by_year
        context['event_year'] = self.kwargs.get('year')
        context['event_month'] = self.kwargs.get('month')
        context['event_day'] = self.kwargs.get('day')
        return context


class EventListView(AppConfigMixin, NavigationMixin, ListView):
    model = Event
    template_name = 'aldryn_events/events_list.html'
    archive = False

    def get_queryset(self):
        qs = (super(EventListView, self).get_queryset()
                                        .namespace(self.namespace))

        language = get_language_from_request(self.request, check_path=True)
        qs = qs.translated(language).language(language)

        if self.archive:
            qs = qs.archive()
        else:
            qs = qs.future()

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        if year:
            qs = qs.filter(start_date__year=year)
        if month:
            qs = qs.filter(start_date__month=month)
        if day:
            qs = qs.filter(start_date__day=day)

        return qs.order_by('start_date', 'start_time', 'end_date', 'end_time')


class EventDetailView(AppConfigMixin, NavigationMixin, CreateView):
    model = Registration
    template_name = 'aldryn_events/events_detail.html'
    form_class = EventRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        language = get_language_from_request(request, check_path=True)
        self.event = (Event.objects.namespace(self.namespace)\
                                   .published()
                                   .translated(language, slug=kwargs['slug'])
                                   .language(language).get())

        setattr(self.request, request_events_event_identifier, self.event)

        if hasattr(request, 'toolbar'):
            request.toolbar.set_object(self.event)

        return super(EventDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        registered_events = (
            self.request.session.get('registered_events', set())
        )
        context['event'] = self.event
        context['already_registered'] = self.event.id in registered_events
        return context

    def form_valid(self, form):
        registration = super(EventDetailView, self).form_valid(form)
        registered_events = set(
            self.request.session.get('registered_events', [])
        )
        registered_events.add(self.event.id)

        # set's are not json serializable
        self.request.session['registered_events'] = list(registered_events)
        return registration

    def get_success_url(self):
        return self.event.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(EventDetailView, self).get_form_kwargs()
        kwargs['event'] = self.event
        kwargs['language_code'] = (
            get_language_from_request(self.request, check_path=True)
        )
        return kwargs


class ResetEventRegistration(AppConfigMixin, FormView):
    form_class = forms.Form

    def dispatch(self, request, *args, **kwargs):
        language = get_language_from_request(request, check_path=True)
        self.event = (
            Event.objects.namespace(self.namespace)
                         .translated(language, slug=kwargs['slug'])
                         .language(language)
                         .get()
        )
        return super(ResetEventRegistration, self).dispatch(request, *args,
                                                            **kwargs)

    def form_valid(self, form):
        registered_events = (
            self.request.session.get('registered_events', set())
        )
        registered_events.remove(self.event.id)
        self.request.session['registered_events'] = registered_events
        return super(ResetEventRegistration, self).form_valid(form)

    def get_success_url(self):
        return reverse('events_detail', kwargs={'slug': self.event.slug})


class EventDatesView(AppConfigMixin, TemplateView):
    template_name = 'aldryn_events/includes/calendar_table.html'

    def get_context_data(self, **kwargs):
        ctx = super(EventDatesView, self).get_context_data(**kwargs)
        if 'year' not in ctx or 'month' not in ctx:
            today = datetime.datetime.today()
            ctx['month'] = today.month
            ctx['year'] = today.year

        current_date = datetime.date(
            day=1, month=int(ctx['month']), year=int(ctx['year'])
        )
        language = get_language_from_request(self.request, check_path=True)
        ctx['days'] = build_calendar(ctx['year'], ctx['month'], language)
        ctx['current_date'] = current_date
        ctx['last_month'] = current_date + datetime.timedelta(days=-1)
        ctx['next_month'] = current_date + datetime.timedelta(days=35)
        return ctx

event_dates = EventDatesView.as_view()
event_detail = EventDetailView.as_view()
event_list = EventListView.as_view()
event_list_archive = EventListView.as_view(archive=True)
reset_event_registration = ResetEventRegistration.as_view()
