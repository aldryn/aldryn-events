# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar

from aldryn_events import request_events_event_identifier


@toolbar_pool.register
class EventsToolbar(CMSToolbar):

    def get_on_delete_redirect_url(self, event):
        return reverse('{0}:events_list'.format(event.app_config.namespace))

    def populate(self):
        if not self.is_current_app:
            return

        def can(action, model):
            perm = 'aldryn_events.%(action)s_%(model)s' % {
                'action': action, 'model': model
            }
            return self.request.user.has_perm(perm)

        if can('add', 'event'):
            menu = self.toolbar.get_or_create_menu('events-app', _('Events'))
            menu.add_modal_item(
                _('Add Event'), reverse('admin:aldryn_events_event_add')
            )

        current = getattr(self.request, request_events_event_identifier, None)

        if current:
            if can('change', 'event'):
                menu = self.toolbar.get_or_create_menu(
                    'events-app', _('Events')
                )
                menu.add_modal_item(
                    _('Edit this event'),
                    reverse(
                        'admin:aldryn_events_event_change', args=(current.pk,)
                    ))

            if can('delete', 'event'):
                redirect_url = self.get_on_delete_redirect_url(current)
                menu = self.toolbar.get_or_create_menu(
                    'events-app', _('Events')
                )
                menu.add_modal_item(
                    _('Delete this event'),
                    reverse(
                        'admin:aldryn_events_event_delete', args=(current.pk,)
                    ),
                    on_close=redirect_url)
