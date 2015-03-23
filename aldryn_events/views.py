# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from django import forms
from django.db.models.query import Q
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from django.utils.translation import get_language_from_request
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
)

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_apphooks_config.utils import get_app_instance
from datetime import date, datetime

from . import request_events_event_identifier
from .forms import EventRegistrationForm
from .models import Event, Registration, EventCalendarPlugin
from .templatetags.aldryn_events import build_calendar_context
from .utils import (
    build_events_by_year,
)


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
            events=(
                Event.objects.namespace(self.namespace)
                             .archive()
                             .translated(language).language(language)
            ),
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

    def get_paginate_by(self, queryset):
        return getattr(
            settings, 'ALDRYN_EVENTS_PAGINATE_BY', self.paginate_by
        )

    def get_queryset(self):
        qs = (super(EventListView, self).get_queryset()
                                        .namespace(self.namespace))

        language = get_language_from_request(self.request, check_path=True)
        qs = qs.translated(language).language(language)

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        if year or month or day:
            tz = get_current_timezone()
            if year and month and day:
                year, month, day = map(int, [year, month, day])
                _date = date(year, month, day)
                last_datetime = datetime(
                    year, month, day, 23, 59, 59, tzinfo=tz
                )

                qs = qs.filter(
                    Q(start_date=_date, end_date__isnull=True) |
                    Q(start_date__lte=_date, end_date__gte=_date)
                ).published(last_datetime)
            elif year and month:
                year, month = map(int, [year, month])
                date_start = date(year, month, 1)
                date_end = date_start + relativedelta(months=1, days=-1)
                last_datetime = datetime(
                    tzinfo=tz, *(date_end.timetuple()[:3])
                ) + relativedelta(days=1, minutes=-1)

                qs = qs.filter(
                    Q(start_date__range=(date_start, date_end),
                      end_date__isnull=True) |
                    Q(start_date__range=(date_start, date_end),
                      end_date__lte=date_end) |
                    Q(start_date__lt=date_start,
                      end_date__range=(date_start, date_end)) |
                    Q(start_date__lt=date_start,
                      end_date__gte=date_end)
                ).published(last_datetime)
            else:
                year = int(year)
                date_start = date(year, 1, 1)
                date_end = date_start + relativedelta(years=1, days=-1)
                last_datetime = datetime(
                    tzinfo=tz, *(date_end.timetuple()[:3])
                ) + relativedelta(days=1, minutes=-1)

                qs = qs.filter(
                    Q(start_date__range=(date_start, date_end),
                      end_date__isnull=True) |
                    Q(start_date__range=(date_start, date_end),
                      end_date__lte=date_end) |
                    Q(start_date__lt=date_start,
                      end_date__range=(date_start, date_end))
                ).published(last_datetime)

        else:
            if self.archive:
                qs = qs.archive()
            else:
                qs = qs.future()

        return qs.order_by('start_date', 'start_time', 'end_date', 'end_time')

    def get_context_data(self, **kwargs):
        if self.config and self.config.app_data.config.show_ongoing_first:
            ongoing_objects = self.object_list.ongoing()
            object_list = self.object_list.exclude(
                pk__in=ongoing_objects.values_list('pk', flat=True)
            )
            kwargs.update({
                'object_list': object_list,
                'ongoing_objects': ongoing_objects
            })
        return super(EventListView, self).get_context_data(**kwargs)


class EventDetailView(AppConfigMixin, NavigationMixin, CreateView):
    model = Registration
    template_name = 'aldryn_events/events_detail.html'
    form_class = EventRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        language = get_language_from_request(request, check_path=True)
        self.event = (Event.objects.namespace(self.namespace)
                                   .published()
                                   .translated(language, slug=kwargs['slug'])
                                   .language(language).get())

        setattr(self.request, request_events_event_identifier,  self.event)

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
        self.namespace, self.config = get_app_instance(request)
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
        ctx['calendar_tag'] = build_calendar_context(
            year, month, language, namespace
        )
        return ctx

event_dates = EventDatesView.as_view()
event_detail = EventDetailView.as_view()
event_list = EventListView.as_view()
event_list_archive = EventListView.as_view(archive=True)
reset_event_registration = ResetEventRegistration.as_view()
