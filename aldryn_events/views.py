# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from itertools import chain

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    # Django 1.6
    from django.contrib.sites.models import get_current_site
from django.http import Http404
from django.utils import timezone
from django.utils.translation import get_language_from_request
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
)

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_apphooks_config.utils import get_app_instance
from datetime import date
from menus.utils import set_language_changer

from . import request_events_event_identifier, ORDERING_FIELDS
from .forms import EventRegistrationForm
from .models import Event, Registration, EventCalendarPlugin, EventsConfig
from .templatetags.aldryn_events import build_calendar_context
from .utils import (
    build_events_by_year, get_event_q_filters, get_valid_languages
)


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang


class NavigationMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.request_language = get_language(request)
        return super(NavigationMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NavigationMixin, self).get_context_data(**kwargs)
        qs = (Event.objects.namespace(self.namespace)
                           .active_translations(self.request_language)
                           .language(self.request_language))
        events_by_year = build_events_by_year(qs.future())
        context['events_by_year'] = events_by_year
        archived_events_by_year = build_events_by_year(qs.archive(),
                                                       is_archive_view=True)
        context['archived_events_by_year'] = archived_events_by_year
        context['event_year'] = self.kwargs.get('year')
        context['event_month'] = self.kwargs.get('month')
        context['event_day'] = self.kwargs.get('day')
        return context


class EventListView(AppConfigMixin, NavigationMixin, ListView):
    model = Event
    template_name = 'aldryn_events/events_list.html'
    archive = False

    def get_paginate_by(self, queryset):
        return getattr(
            settings, 'ALDRYN_EVENTS_PAGINATE_BY', self.paginate_by
        )

    def get_queryset(self):
        # do not fail and do not try to resolve events if corresponding
        # EventsConfig does not exist (rare situation)
        if not EventsConfig.objects.filter(namespace=self.namespace).exists():
            qs = Event.objects.none()
        else:
            qs = (super(EventListView, self).get_queryset()
                                            .namespace(self.namespace))
        if not self.request.GET.get('all_languages', False):
            qs = qs.active_translations(self.request_language).language(
                self.request_language)

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        # prepare language properties for filtering
        site_id = getattr(get_current_site(self.request), 'id', None)
        valid_languages = get_valid_languages(
            self.namespace, self.request_language, site_id)

        self.archive_qs = []

        if year or month or day:
            if year and month and day:
                year, month, day = map(int, [year, month, day])
                first_date = last_date = date(year, month, day)

            elif year and month:
                year, month = map(int, [year, month])
                first_date = date(year, month, 1)
                last_date = first_date + relativedelta(months=1, days=-1)

            else:
                year = int(year)
                first_date = date(year, 1, 1)
                last_date = first_date + relativedelta(years=1, days=-1)

            filter_args = get_event_q_filters(first_date, last_date)
            qs = qs.filter(filter_args).published()
        else:
            if self.archive:
                qs = qs.archive()
            else:
                self.archive_qs = (qs.archive()
                                     .translated(*valid_languages)
                                     .order_by(*ORDERING_FIELDS))
                qs = qs.future()

        qs = qs.translated(*valid_languages)
        return qs.order_by(*ORDERING_FIELDS).distinct()

    def get_context_data(self, **kwargs):
        object_list = self.object_list

        if self.config and self.config.app_data.config.show_ongoing_first:
            ongoing_objects = self.object_list.ongoing()
            object_list = object_list.exclude(
                pk__in=ongoing_objects.values_list('pk', flat=True)
            )
            kwargs['ongoing_objects'] = ongoing_objects

        # add outdated events to end of list
        def make_outdated(obj):
            obj.is_outdated = True
            return obj
        object_list = list(chain(object_list, map(make_outdated,
                                                  self.archive_qs)))
        kwargs['object_list'] = object_list

        return super(EventListView, self).get_context_data(**kwargs)


class EventDetailView(AppConfigMixin, NavigationMixin, CreateView):
    model = Registration
    template_name = 'aldryn_events/events_detail.html'
    form_class = EventRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        self.request_language = get_language(request)
        qs = (Event.objects.namespace(self.namespace)
                           .published()
                           .language(self.request_language))
        site_id = getattr(get_current_site(request), 'id', None)
        valid_languages = get_valid_languages(
            self.namespace, self.request_language, site_id)
        self.queryset = qs.translated(*valid_languages).order_by(
            *ORDERING_FIELDS)
        self.event = self.queryset.active_translations(
            self.request_language, slug=kwargs['slug']).first()
        if not self.event:
            raise Http404("Event not found")

        set_language_changer(request, self.event.get_absolute_url)
        setattr(self.request, request_events_event_identifier, self.event)

        if hasattr(request, 'toolbar'):
            request.toolbar.set_object(self.event)

        return super(EventDetailView, self).dispatch(request, *args, **kwargs)

    def get_neighbors_events(self):
        qs = list(self.queryset)
        length = len(qs)
        _prev, _next = None, None

        try:
            index = qs.index(self.event)
        except ValueError:
            # That should not happen, but since this method just help populate
            # the context, we don't allow it to fail
            pass
        else:
            if index - 1 >= 0:
                _prev = qs[index - 1]
            if index + 1 < length:
                _next = qs[index + 1]

        return _prev, _next

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        registered_events = (
            self.request.session.get('registered_events', set())
        )
        context['event'] = self.event
        context['already_registered'] = self.event.id in registered_events
        _prev, _next = self.get_neighbors_events()
        context.update({'prev_event': _prev, 'next_event': _next})
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
        self.namespace, self.config = get_app_instance(request)
        language = get_language_from_request(request, check_path=True)
        self.event = (
            Event.objects.namespace(self.namespace)
                         .active_translations(language, slug=kwargs['slug'])
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
        url_name = '{0}:events_detail'.format(self.namespace)
        return reverse(
            url_name, kwargs={'slug': self.event.slug},
            current_app=self.namespace
        )


class EventDatesView(AppConfigMixin, TemplateView):
    template_name = 'aldryn_events/includes/calendar_table.html'

    def get_context_data(self, **kwargs):
        ctx = super(EventDatesView, self).get_context_data(**kwargs)

        today = timezone.now().date()
        year = ctx.get('year', today.year)
        month = ctx.get('month', today.month)

        # Get plugin if possible so we can use language and namespace from
        # plugin, if not possible get namespace from view, language from
        # request
        try:
            pk = self.request.GET['plugin_pk'] or None
            plugin = EventCalendarPlugin.objects.get(pk=pk)
        except (EventCalendarPlugin.DoesNotExist, KeyError):
            namespace = self.namespace
            language = get_language_from_request(self.request, check_path=True)
        else:
            namespace = plugin.app_config.namespace
            language = plugin.language

        # calendar is the calendar tag
        site_id = getattr(get_current_site(self.request), 'id', None)
        ctx['calendar_tag'] = build_calendar_context(
            year, month, language, namespace, site_id
        )
        return ctx

event_dates = EventDatesView.as_view()
event_detail = EventDetailView.as_view()
event_list = EventListView.as_view()
event_list_archive = EventListView.as_view(archive=True)
reset_event_registration = ResetEventRegistration.as_view()
