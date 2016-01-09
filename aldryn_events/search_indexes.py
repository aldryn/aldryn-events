# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext

from aldryn_search.utils import get_index_base, strip_tags
from parler.utils.context import switch_language
from .models import Event


class EventsIndex(get_index_base()):
    haystack_use_for_indexing = getattr(settings, "ALDRYN_EVENTS_SEARCH", True)

    INDEX_TITLE = True

    def prepare_pub_date(self, obj):
        return obj.publish_at

    def get_description(self, obj):
        with switch_language(obj):
            return obj.safe_translation_getter('short_description')

    def get_title(self, obj):
        with switch_language(obj):
            return obj.safe_translation_getter('title')

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_index_kwargs(self, language):
        return {'translations__language_code': language}

    def get_index_queryset(self, language):
        return (
            self.get_model().objects.published()
                                    .language(language)
                                    .active_translations(language)
        )

    def get_model(self):
        return Event

    def get_search_data(self, obj, language, request):
        description = self.get_description(obj) or ''
        text_bits = [strip_tags(description)]
        plugins = obj.description.cmsplugin_set.filter(language=language)
        for base_plugin in plugins:
            try:
                instance, plugin_type = base_plugin.get_plugin_instance()
                if instance is not None:
                    content = strip_tags(
                        instance.render_plugin(context=RequestContext(request))
                    )
                    text_bits.append(content)
            except Exception:
                # avoid that bad plugins breaks entire indexer
                # TODO: logging
                pass
        return ' '.join(text_bits)
