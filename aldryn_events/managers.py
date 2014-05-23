# -*- coding: utf-8 -*-
from django.utils.translation import get_language
from django.utils import timezone

from cms.utils.i18n import get_language_code

from hvad.models import TranslationManager


class EventManager(TranslationManager):

    def published(self, now=None):
        now = now or timezone.now()
        # we call get_language_code to make sure that the current language
        # is in the settings.py. This is a known django bug.
        language = get_language_code(language_code=get_language())
        return self.language(language).filter(is_published=True, publish_at__lte=now)

    def upcoming(self, count, now=None):
        now = now or timezone.now()
        return self.future(now=now)[:count]

    def past(self, count, now=None):
        now = now or timezone.now()
        return self.archive(now=now)[:count]

    def future(self, now=None):
        """
        includes all events that are not over yet
        """
        now = now or timezone.now()
        return self.published(now=now).filter(end_at__gte=now).order_by('start_at', 'end_at', 'slug')

    def archive(self, now=None):
        """
        includes all events that have ended
        """
        now = now or timezone.now()
        return self.published(now=now).filter(end_at__lt=now).order_by('-start_at', 'end_at', 'slug')