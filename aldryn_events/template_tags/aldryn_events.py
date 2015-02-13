# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template
from django.utils.dates import MONTHS
from django.utils.timezone import now
from aldryn_events.models import EventsConfig
from aldryn_events.utils import build_calendar

register = template.Library()


# class CalendarNode(template.Node):
#     """
#     Renders a template with a calendar of events
#     """
#     def __init__(self):
#         pass
#
#     def render(self, context):
#         pass
#

@register.inclusion_tag('aldryn_events/tags/calendar.html', takes_context=True)
def calendar(year, month, language, namespace=None):
    current_date = now().today().replace(day=1)
    if namespace:
        try:
            app_config = EventsConfig.objects.get(namespace=namespace)
        except EventsConfig.DoesNotExist:
            raise template.TemplateSyntaxError(
                "'namespace' must be a existent EventConfig namespace, "
                "not '{0}'.".format(namespace)
            )

    context = {
        'current_date': current_date,
        'last_month': current_date - timedelta(month=1),
        'next_month': current_date + timedelta(month=1),
        'label': "{} {}".format(MONTHS.get(int(month)), year)
    }
    context['calendar'] = build_calendar(year, month, language, namespace)
    return context
