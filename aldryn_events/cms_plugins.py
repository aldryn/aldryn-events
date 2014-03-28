import datetime
from itertools import groupby
from operator import attrgetter

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .utils import get_monthdates
from .models import UpcomingPluginItem, Event
from .forms import UpcomingPluginForm


class UpcomingPlugin(CMSPluginBase):
    render_template = False
    name = _('Upcoming')
    module = _('Events')
    model = UpcomingPluginItem
    form = UpcomingPluginForm

    def render(self, context, instance, placeholder):
        context['events'] = Event.objects.upcoming(count=instance.latest_entries)
        self.render_template = 'aldryn_events/plugins/upcoming/%s/upcoming.html' % instance.style
        return context

plugin_pool.register_plugin(UpcomingPlugin)


class CalendarPlugin(CMSPluginBase):
    render_template = 'aldryn_events/plugins/calendar.html'
    name = _('Calendar')
    module = _('Events')

    def build_calendar(self, instance):
        today = datetime.datetime.today()
        # Get a list of all dates in this month (with pre/succedding for nice layout)
        monthdates = [(x, None) for x in get_monthdates(today.month, today.year)]
        # get all upcoming events, ordered by start_date
        events = groupby(Event.objects.published().filter(start_date__gte=monthdates[0][0], start_date__lte=monthdates[-1][0]).order_by('start_date'), attrgetter('start_date'))
        # group events by starting_date
        grouped_events = [(date, list(event_list)) for date, event_list in events]
        # merge events into monthdates
        for date, event_list in grouped_events:
            index = monthdates.index((date, None))
            monthdates[index] = (date, event_list)
        return monthdates

    def render(self, context, instance, placeholder):
        context['days'] = self.build_calendar(instance)
        context['today'] = datetime.datetime.today()
        context['current_month'] = str(datetime.datetime.today().month)
        return context

plugin_pool.register_plugin(CalendarPlugin)
