# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool

from .models import EventsConfig


class EventListAppHook(CMSConfigApp):
    app_name = 'aldryn_events'
    app_config = EventsConfig
    name = _('Events')
    urls = ['aldryn_events.urls']

apphook_pool.register(EventListAppHook)
