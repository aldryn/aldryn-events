from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

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
