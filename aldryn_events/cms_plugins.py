import datetime

from django.utils import timezone
from django.utils.dates import MONTHS
from django.utils.translation import (
    ugettext_lazy as _, get_language_from_request
)

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .utils import build_calendar, namespace_is_apphooked
from .models import (
    UpcomingPluginItem, Event, EventListPlugin, EventCalendarPlugin
)

from .forms import (
    UpcomingPluginForm, EventListPluginForm, EventCalendarPluginForm,
)


NO_APPHOOK_ERROR_MESSAGE = _(
    'There is an error in plugin configuration: selected Events '
    'config is not available. Please switch to edit mode and '
    'change plugin app_config settings to use valid config. '
    'Also note that aldryn-events should be used at least once '
    'as an apphook for that config.')


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
        self.render_template = (
            'aldryn_events/plugins/upcoming/%s/upcoming.html' % instance.style
        )
        context['instance'] = instance
        # check if we can reverse list view for configured namespace
        # if no prepare a message to admin users.
        if not namespace_is_apphooked(namespace):
            # add message, should be properly handled in template
            context['plugin_configuration_error'] = NO_APPHOOK_ERROR_MESSAGE
            return context

        events = (Event.objects.namespace(namespace)
                               .active_translations(language)
                               .language(language))

        if instance.past_events:
            events = events.past(count=instance.latest_entries)
        else:
            events = events.upcoming(count=instance.latest_entries)

        context['events'] = events
        return context

plugin_pool.register_plugin(UpcomingPlugin)


class EventListCMSPlugin(CMSPluginBase):
    render_template = False
    module = _('Events')
    name = _('List')
    model = EventListPlugin
    form = EventListPluginForm

    def render(self, context, instance, placeholder):
        self.render_template = (
            'aldryn_events/plugins/list/%s/list.html' % instance.style
        )
        language = (
            instance.language or
            get_language_from_request(context['request'], check_path=True)
        )
        context['instance'] = instance

        namespace = instance.app_config_id and instance.app_config.namespace
        # check if we can reverse list view for configured namespace
        # if no prepare a message to admin users.
        if not namespace_is_apphooked(namespace):
            # add message, should be properly handled in template
            context['plugin_configuration_error'] = NO_APPHOOK_ERROR_MESSAGE
            return context
        # With Django 1.5 and because a bug in SortedManyToManyField
        # we can not use instance.events or we get a error like:
        # DatabaseError:
        #   no such column: aldryn_events_eventlistplugin_events.sort_value
        events = (Event.objects.namespace(namespace)
                               .active_translations(language)
                               .language(language)
                               .filter(eventlistplugin__pk=instance.pk))

        context['events'] = events
        return context

plugin_pool.register_plugin(EventListCMSPlugin)


class CalendarPlugin(CMSPluginBase):
    render_template = 'aldryn_events/plugins/calendar.html'
    name = _('Calendar')
    module = _('Events')
    cache = False
    model = EventCalendarPlugin
    form = EventCalendarPluginForm

    def render(self, context, instance, placeholder):
        # # check if we can reverse list view for configured namespace
        # # if no prepare a message to admin users.
        namespace = instance.app_config_id and instance.app_config.namespace
        if not namespace_is_apphooked(namespace):
            # add message, should be properly handled in template
            context['plugin_configuration_error'] = NO_APPHOOK_ERROR_MESSAGE
            return context

        year = context.get('event_year')
        month = context.get('event_month')

        if not all([year, month]):
            year = str(timezone.now().date().year)
            month = str(timezone.now().date().month)

        current_date = datetime.date(int(year), int(month), 1)
        language = instance.language

        context['event_year'] = year
        context['event_month'] = month
        context['days'] = build_calendar(year, month, language, namespace)
        context['current_date'] = current_date
        context['last_month'] = current_date + datetime.timedelta(days=-1)
        context['next_month'] = current_date + datetime.timedelta(days=35)
        context['calendar_label'] = u'%s %s' % (MONTHS.get(int(month)), year)
        context['calendar_namespace'] = namespace
        context['calendar_language'] = language
        return context

plugin_pool.register_plugin(CalendarPlugin)
