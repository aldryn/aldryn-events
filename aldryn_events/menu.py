# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import (
    get_language_from_request,
    ugettext_lazy as _,
)

from cms.menu_bases import CMSAttachMenu
from cms.apphook_pool import apphook_pool
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Event


class EventsMenu(CMSAttachMenu):
    name = _('Events')

    def get_nodes(self, request):
        nodes = []
        language = get_language_from_request(request, check_path=True)
        events = (Event.objects.published()
                               .language(language)
                               .active_translations(language))

        if hasattr(self, 'instance') and self.instance:
            # If self has a property `instance`, then we're using django CMS
            # 3.0.12 or later, which supports using CMSAttachMenus on multiple,
            # apphook'ed pages, each with their own apphook configuration. So,
            # here we modify the queryset to reflect this.
            app = apphook_pool.get_apphook(self.instance.application_urls)
            if app:
                events = events.namespace(self.instance.application_namespace)

        for event in events:
            try:
                url = event.get_absolute_url(language=language)
            except NoReverseMatch:
                url = None

            if url:
                node = NavigationNode(
                    event.title,
                    event.get_absolute_url(language=language),
                    event.pk,
                )
                nodes.append(node)

        return nodes

menu_pool.register_menu(EventsMenu)
