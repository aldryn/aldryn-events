import datetime

from django.conf.urls import patterns, url
from django.utils import timezone
from django.utils.dates import MONTHS
from django.utils.translation import (
    ugettext_lazy as _, get_language_from_request
)

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .views import EventDatesView
from .utils import build_calendar
from .models import (
    UpcomingPluginItem, Event, EventListPlugin, EventCalendarPlugin
)

from .forms import UpcomingPluginForm


class UpcomingPlugin(CMSPluginBase):
    render_template = False
    name = _('Upcoming or Past Events')
    module = _('Events')
    model = UpcomingPluginItem
    form = UpcomingPluginForm

    def render(self, context, instance, placeholder):
        # translated filter the events, language set current language
        language = get_language_from_request(context['request'],
                                             check_path=True)
        namespace = instance.app_config_id and instance.app_config.namespace

        events = (Event.objects.namespace(namespace)
                               .translated(language)
                               .language(language))

        if instance.past_events:
            events = events.past(count=instance.latest_entries)
        else:
            events = events.upcoming(count=instance.latest_entries)

        context['events'] = events
        context['instance'] = instance
        self.render_template = (
            'aldryn_events/plugins/upcoming/%s/upcoming.html' % instance.style
        )
        return context

plugin_pool.register_plugin(UpcomingPlugin)


class EventListCMSPlugin(CMSPluginBase):
    render_template = False
    module = _('Events')
    name = _('List')
    model = EventListPlugin

    def render(self, context, instance, placeholder):
        self.render_template = (
            'aldryn_events/plugins/list/%s/list.html' % instance.style
        )
        language = (
            instance.language or
            get_language_from_request(context['request'], check_path=True)
        )

        namespace = instance.app_config_id and instance.app_config.namespace
        # With Django 1.5 and because a bug in SortedManyToManyField
        # we can not use instance.events or we get a error like:
        # DatabaseError: no such column: aldryn_events_eventlistplugin_events.sort_value
        events = (Event.objects.namespace(namespace)
                               .translated(language)
                               .language(language)
                               .filter(eventlistplugin__pk=instance.pk))

        context['instance'] = instance
        context['events'] = events

        return context

plugin_pool.register_plugin(EventListCMSPlugin)


class CalendarPlugin(CMSPluginBase):
    render_template = 'aldryn_events/plugins/calendar.html'
    name = _('Calendar')
    module = _('Events')
    cache = False
    model = EventCalendarPlugin

    def render(self, context, instance, placeholder):
        year = context.get('event_year')
        month = context.get('event_month')

        if not all([year, month]):
            year = str(timezone.now().date().year)
            month = str(timezone.now().date().month)

        current_date = datetime.date(
            day=1, month=int(month), year=int(year)
        )
        language = get_language_from_request(
            context['request'], check_path=True
        )
        namespace = instance.app_config_id and instance.app_config.namespace
        context['days'] = build_calendar(year, month, language, namespace)
        context['current_date'] = current_date
        context['last_month'] = current_date + datetime.timedelta(days=-1)
        context['next_month'] = current_date + datetime.timedelta(days=35)
        context['calendar_label'] = u'%s %s' % (MONTHS.get(int(month)), year)

        return context

    def get_plugin_urls(self):
        return patterns('',  # NOQA
            url(r'^get-dates/$', EventDatesView.as_view(),
                name='get-calendar-dates'),
            url(r'^get-dates/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
                EventDatesView.as_view(), name='get-calendar-dates'),
        )


plugin_pool.register_plugin(CalendarPlugin)
