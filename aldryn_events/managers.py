# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils import timezone

from parler.managers import TranslatableManager, TranslatableQuerySet


class EventQuerySet(TranslatableQuerySet):

    def namespace(self, namespace):
        """
        Filter by app_config namespace
        """
        return self.filter(app_config__namespace=namespace)

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
                    .order_by('-start_date', '-start_time', 'end_date',
                              'end_time', 'translations__slug'))

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
                    .order_by('start_date', 'start_time', 'end_date',
                              'end_time', 'translations__slug'))

    def published(self, now=None):
        now = now or timezone.now()
        return self.filter(is_published=True, publish_at__lte=now)


class EventManager(TranslatableManager):
    queryset_class = EventQuerySet

    def namespace(self, namespace):
        return self.get_queryset().namespace(namespace)

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
