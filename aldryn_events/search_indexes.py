# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext

from aldryn_events.models import Event


try:
    from aldryn_search.utils import get_index_base, strip_tags
except ImportError:
    # celery tasks shouldn't fail if aldryn_events and haystack but aldryn_search is installed
    pass
else:

    class EventsIndex(get_index_base()):
        haystack_use_for_indexing = getattr(settings, "ALDRYN_EVENTS_SEARCH", True)

        INDEX_TITLE = True

        def prepare_pub_date(self, obj):
            return obj.publish_at

        def get_description(self, obj):
            return obj.short_description

        def get_title(self, obj):
            return obj.title

        def get_index_kwargs(self, language):
            return {'translations__language_code': language}

        def get_index_queryset(self, language):
            return self.get_model().objects.published().all()

        def get_model(self):
            return Event

        def get_search_data(self, obj, language, request):
            description = self.get_description(obj)
            text_bits = [strip_tags(description)]
            plugins = obj.description.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                instance, plugin_type = base_plugin.get_plugin_instance()
                if not instance is None:
                    content = strip_tags(instance.render_plugin(context=RequestContext(request)))
                    text_bits.append(content)
            return ' '.join(text_bits)
