# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _

from cms.apphook_pool import apphook_pool
from cms.app_base import CMSApp


class EventListAppHook(CMSApp):
    name = _('Events')
    app_name = 'aldryn_events'
    urls = ['aldryn_events.urls']

apphook_pool.register(EventListAppHook)
