# -*- coding: utf-8 -*-

from datetime import timedelta, date

from django import template
from django.template.loader import get_template
from django.utils.dates import MONTHS
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..models import EventsConfig
from ..utils import build_calendar

register = template.Library()


ERROR_MESSAGE = _(
    'Seems that EventsConfig for this page is missing. Tried to look for {0}. '
    'To be able to see calendar and events againg - you need to create or '
    'select another EventsConfig for this page.'
)


@register.simple_tag(takes_context=True)
def calendar(context, year, month, language, namespace):
    template_name = 'aldryn_events/includes/calendar.html'

    t = get_template(template_name)
    try:
        EventsConfig.objects.get(namespace=namespace)
    except EventsConfig.DoesNotExist:
        context['namespace_error'] = ERROR_MESSAGE.format(namespace)
    else:
        context['calendar_tag'] = build_calendar_context(
            year, month, language, namespace)
    rendered = t.render(context)
    return rendered


def build_calendar_context(year, month, language, namespace):
    # if not have a selected date
    today = timezone.now().date()
    if not all([year, month]):
        year = today.year
        month = today.month

    year, month = int(year), int(month)
    current_date = date(year, month, 1)

    context = {
        'today': today,
        'current_date': current_date,
        'last_month': current_date - timedelta(days=1),
        'next_month': (current_date + timedelta(days=31)).replace(day=1),
        'label': u"{0} {1}".format(MONTHS.get(int(month)), year),
        'namespace': namespace
    }

    # add css classes here instead in template
    # TODO: can configure css classes in appconfig ;)
    _calendar = build_calendar(year, month, language, namespace)
    calendar_list = []
    for day, events in _calendar.items():
        css = []
        if events:
            for event in events:
                if event.start_date == day:
                    css.append('events')
                    break
            else:
                css.append('multiday-events')
        if day.weekday() in [5, 6]:
            css.append('weekend')
        if day == today:
            css.append('today')
        # disable days that isn't from this month
        if day <= context['last_month'] or day >= context['next_month']:
            css.append('disabled')
        calendar_list.append((day, events, ' '.join(css)))
    context['calendar'] = calendar_list
    return context
