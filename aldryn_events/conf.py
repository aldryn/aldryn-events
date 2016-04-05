# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from appconf import AppConf


class EventsAppConf(AppConf):

    TEASER_TEMPLATE_CHOICES = (
        ('default', _('default')),
    )
    USER_REGISTRATION_EMAIL = False
    MANAGER_REGISTRATION_EMAIL = False
    MANAGERS = None
    DEFAULT_FROM_EMAIL = None
    PLUGIN_CACHE_TIMEOUT = 900

    def configure_managers(self, value):
        if value is None:
            return settings.MANAGERS
        return value

    def configure_default_from_email(self, value):
        if value is None:
            return settings.DEFAULT_FROM_EMAIL
        return value
