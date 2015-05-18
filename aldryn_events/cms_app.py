# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool

from .models import EventsConfig
from .menu import EventsMenu


class EventListAppHook(CMSConfigApp):
    app_name = 'aldryn_events'
    app_config = EventsConfig
    menus = [EventsMenu]
    name = _('Events')
    urls = ['aldryn_events.urls']

apphook_pool.register(EventListAppHook)
