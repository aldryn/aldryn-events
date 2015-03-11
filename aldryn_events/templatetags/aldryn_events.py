# -*- coding: utf-8 -*-

from datetime import timedelta, date

from django import template
from django.utils.dates import MONTHS
from django.utils import timezone
from sekizai.context import SekizaiContext

from ..models import EventsConfig
from ..utils import build_calendar

register = template.Library()


@register.inclusion_tag('aldryn_events/tags/calendar.html',
                        context_class=SekizaiContext)
def calendar(year, month, language, namespace):
    # if not have a selected date
    today = timezone.now().date()
    if not all([year, month]):
        year = today.year
        month = today.month

    year, month = int(year), int(month)
    current_date = date(year, month, 1)

    if namespace:
        try:
            app_config = EventsConfig.objects.get(namespace=namespace)
        except EventsConfig.DoesNotExist:
            raise template.TemplateSyntaxError(
                "'namespace' must be a existent EventConfig namespace, "
                "not '{0}'.".format(namespace)
            )

    context = {
        'today': today,
        'current_date': current_date,
        'last_month': current_date - timedelta(days=1),
        'next_month': (current_date + timedelta(days=31)).replace(day=1),
        'calendar_label': "{0} {1}".format(MONTHS.get(int(month)), year)
    }

    # add css classes here instead in template
    # TODO: can configure css classes in appconfig ;)
    _calendar = build_calendar(year, month, language, namespace)

    calendar_list = []
    for day, events in _calendar.items():
        css = []
        if events:
            css.append('events')
        if day.isoweekday() in [0, 6]:
            css.append('weekend')
        if day == today:
            css.append('today')
        # disable days that isn't from this month
        if day <= context['last_month'] or day >= context['next_month']:
            css.append('disabled')
        calendar_list.append((day, events, ' '.join(css)))
    context['calendar'] = calendar_list
    return context
