from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import UpcomingPluginItem, Event


class UpcomingPlugin(CMSPluginBase):

    render_template = 'aldryn_events/plugins/upcoming.html'
    name = _('Upcoming')
    module = _('Events')
    model = UpcomingPluginItem

    def render(self, context, instance, placeholder):
        count = instance.latest_entries
        context['events'] = Event.objects.upcoming(count=count)
        return context

plugin_pool.register_plugin(UpcomingPlugin)