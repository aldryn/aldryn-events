# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.translation import (
    ugettext_lazy as _,
    get_language_from_request,
)

from aldryn_apphooks_config.utils import get_app_instance
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from parler.models import TranslatableModel

from .models import Event
from .cms_appconfig import EventsConfig


def get_obj_from_request(model, request, pk_url_kwarg='pk',
                         slug_url_kwarg='slug', slug_field='slug'):
    """
    Given a model and the request, try to extract and return an object
    from an available 'pk' or 'slug', or return None.

    Note that no checking is done that the view's kwargs really are for objects
    matching the provided model (how would it?) so use only where appropriate.
    """
    language = get_language_from_request(request, check_path=True)
    kwargs = request.resolver_match.kwargs
    mgr = model.objects
    if pk_url_kwarg in kwargs:
        return mgr.filter(pk=kwargs[pk_url_kwarg]).first()
    elif slug_url_kwarg in kwargs:
        # If the model is translatable, and the given slug is a translated
        # field, then find it the Parler way.
        filter_kwargs = {slug_field: kwargs[slug_url_kwarg]}
        translated_fields = model._parler_meta.get_translated_fields()
        if (issubclass(model, TranslatableModel) and
                slug_url_kwarg in translated_fields):
            return mgr.active_translations(language, **filter_kwargs).first()
        else:
            # OK, do it the normal way.
            return mgr.filter(**filter_kwargs).first()
    else:
        return None


def get_admin_url(action, action_args=[], **url_args):
    """
    Convenience method for constructing admin-urls with GET parameters.
    """
    base_url = admin_reverse(action, args=action_args)
    # Converts [{key: value}, …] => ["key=value", …]
    url_arg_list = sorted(url_args.iteritems())
    params = ["=".join([str(k), str(v)]) for (k, v) in url_arg_list]
    if params:
        return "?".join([base_url, "&".join(params)])
    else:
        return base_url


@toolbar_pool.register
class EventsToolbar(CMSToolbar):

    def get_on_delete_redirect_url(self, event):
        return reverse('{0}:events_list'.format(event.app_config.namespace))

    def get_app_config(self, config_model):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, config_model):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def populate(self):
        config = self.get_app_config(EventsConfig)

        if not config:
            return

        event = get_obj_from_request(Event, self.request)

        if self.request.user:
            user = self.request.user

            chg_event_perm = user.has_perm('aldryn_events.change_event')
            add_event_perm = user.has_perm('aldryn_events.add_event')
            del_event_perm = user.has_perm('aldryn_events.delete_event')
            chg_config_perm = user.has_perm(
                'aldryn_events.change_eventsconfig')
            add_config_perm = user.has_perm('aldryn_events.add_eventsconfig')

            event_perms = [chg_event_perm, add_event_perm, del_event_perm]
            config_perms = [chg_config_perm, add_config_perm]

            if any(event_perms + config_perms):
                menu = self.toolbar.get_or_create_menu(
                    'events-app', _('Events'))

                if chg_config_perm:
                    url = admin_reverse('aldryn_events_eventsconfig_change',
                                        args=[config.pk, ])
                    menu.add_modal_item(_('Edit App Configuration'), url=url)

                if chg_config_perm and any(event_perms):
                    menu.add_break()

                if chg_event_perm:
                    url = admin_reverse('aldryn_events_event_changelist')
                    menu.add_sideframe_item(_('Events list'), url=url)

                if add_event_perm:
                    url = admin_reverse('aldryn_events_event_add')
                    menu.add_modal_item(_('Add event'), url=url)

                if chg_event_perm and event:
                    url = admin_reverse('aldryn_events_event_change',
                                        args=[event.pk, ])
                    menu.add_modal_item(_('Edit event'), url=url, active=True)

                if del_event_perm and event:
                    redirect_url = self.get_on_delete_redirect_url(event)
                    url = admin_reverse('aldryn_events_event_delete',
                                        args=[event.pk, ])
                    menu.add_modal_item(_('Delete event'), url=url,
                                        on_close=redirect_url)
