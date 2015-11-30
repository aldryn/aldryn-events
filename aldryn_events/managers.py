# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils import timezone

from aldryn_apphooks_config.managers.parler import (
    AppHookConfigTranslatableManager, AppHookConfigTranslatableQueryset
)

from .cms_appconfig import EventsConfig

from . import ARCHIVE_ORDERING_FIELDS, ORDERING_FIELDS


class EventQuerySet(AppHookConfigTranslatableQueryset):

    def upcoming(self, count, now=None):
        now = now or timezone.now()
        return self.future(now=now)[:count]

    def past(self, count, now=None):
        now = now or timezone.now()
        return self.archive(now=now)[:count]

    def archive(self, now=None):
        """
        includes all events that have ended
        """
        now = now or timezone.now()
        today = now.date()
        q_with_end_date = Q(end_date__lt=today)
        q_without_end_date = Q(end_date__isnull=True, start_date__lt=today)
        return (self.published(now=now)
                    .filter(q_with_end_date | q_without_end_date)
                    .order_by(*ARCHIVE_ORDERING_FIELDS))

    def future(self, now=None):
        """
        includes all events that are not over yet. If there is an end_date,
        the event is not over until end_date is over. Otherwise we use
        start_date.
        """
        now = now or timezone.now()
        today = now.date()
        q_with_end_date = Q(end_date__gte=today)
        q_without_end_date = Q(end_date__isnull=True, start_date__gte=today)
        return (self.published(now=now)
                    .filter(q_with_end_date | q_without_end_date)
                    .order_by(*ORDERING_FIELDS))

    def published(self, now=None):
        now = now or timezone.now()
        return self.filter(is_published=True, publish_at__lte=now)

    def ongoing(self, now=None):
        now = now or timezone.now()
        _date = now.date()
        return self.published(now).filter(
            Q(start_date__lte=_date),
            Q(end_date__isnull=True) | Q(end_date__gte=_date)
        )

    def namespace(self, namespace, to=None):
        """
        Overrides the 'normal' namespace QS to also use the 'latest_first'
        flag on the namespace to set the ordering accordingly.
        """
        qs = super(EventQuerySet, self).namespace(namespace, to)
        app = EventsConfig.objects.filter(namespace=namespace).first()
        if app and app.latest_first:
            qs = qs.reverse()
        return qs


class EventManager(AppHookConfigTranslatableManager):

    def get_queryset(self):
        return EventQuerySet(self.model, using=self.db)

    get_query_set = get_queryset

    def upcoming(self, count, now=None):
        return self.get_queryset().upcoming(count, now=now)

    def past(self, count, now=None):
        return self.get_queryset().past(count, now=now)

    def archive(self, now=None):
        return self.get_queryset().archive(now=now)

    def future(self, now=None):
        return self.get_queryset().future(now=now)

    def published(self, now=None):
        return self.get_queryset().published(now=now)

    def ongoing(self, now=None):
        return self.get_queryset().ongoing(now=now)
