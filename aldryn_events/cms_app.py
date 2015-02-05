# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool

from .models import EventsConfig


class EventListAppHook(CMSConfigApp):
    name = _('Events')
    app_name = 'aldryn_events'
    urls = ['aldryn_events.urls']
    app_config = EventsConfig

apphook_pool.register(EventListAppHook)
