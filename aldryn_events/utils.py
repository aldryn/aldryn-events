# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import calendar

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.datastructures import SortedDict
from django.conf import settings


def build_months(year, is_archive_view=False):
    months = SortedDict()
    month_numbers = range(1, 12 + 1)

    if is_archive_view:
        month_numbers = list(reversed(month_numbers))

    for month in month_numbers:
        months[month] = {
            'year': year,
            'month': month,
            'date': date(year, month, 1),
            'events': []
        }
    return months


def group_events_by_year(events):
    """
    Given a queryset of event objects,
    returns a sorted dictionary mapping years to event objects.
    """
    years = SortedDict()

    for event in events:
        year = event.start_date.year
        if year not in years:
            years[year] = [event]
        else:
            years[year].append(event)
    return years


def build_events_by_year(events, **config):
    display_months_without_events = (
        config.get('display_months_without_events', True)
    )

    # archive view means time runs in reverse. of the current year in a
    # other order
    is_archive_view = config.get('is_archive_view', False)
    now = timezone.now()

    events_by_year = SortedDict()
    for event in events:
        year = event.start_date.year
        if year not in events_by_year:
            events_by_year[year] = {
                'year': year,
                'date': date(year, 1, 1),
                'months': build_months(year=year,
                                       is_archive_view=is_archive_view)
            }
        (
            events_by_year[year]['months'][event.start_date.month]['events']
            .append(event)
        )
    flattened_events_by_year = events_by_year.values()
    for year in flattened_events_by_year:
        year['months'] = year['months'].values()
        year['event_count'] = 0
        for month in year['months']:
            month['event_count'] = len(month['events'])
            year['event_count'] += month['event_count']
            month['has_events'] = bool(month['event_count'])
            month['display_in_navigation'] = (
                (not display_months_without_events and month['has_events']) or
                display_months_without_events
            )

        # if this is the current year, hide months before this month (or after
        # this month if we're in archive view)
        if year['year'] == now.year:
            if is_archive_view:
                # don't display any months after the current month
                for month in year['months']:
                    if month['month'] > now.month:
                        month['display_in_navigation'] = False
            else:
                # don't display any months before the current month
                for month in year['months']:
                    if month['month'] < now.month:
                        month['display_in_navigation'] = False
    return flattened_events_by_year


def send_user_confirmation_email(registration, language):
    event = registration.event
    ctx = {
        'event_name': event.title,
        'first_name': registration.first_name,
        'event_url': u"http://%s%s" % (
            Site.objects.get_current(), event.get_absolute_url()
        ),
    }
    subject = render_to_string(
        template_name='aldryn_events/emails/registrant_confirmation.subject.txt',  # NOQA
        dictionary=ctx
    )
    body = render_to_string(
        template_name='aldryn_events/emails/registrant_confirmation.body.txt',
        dictionary=ctx
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
              recipient_list=[registration.email])


def send_manager_confirmation_email(registration, language, emails):
    event = registration.event
    ctx = {
        'event_name': event.title,
        'first_name': registration.first_name,
        'event_url': u"http://%s%s" % (
            Site.objects.get_current(), event.get_absolute_url()
        ),
        'registration_admin_url': u"http://%s%s" % (
            Site.objects.get_current(),
            reverse('admin:aldryn_events_registration_change',
                    args=[str(registration.pk)])
        ),
    }
    subject = render_to_string(
        template_name='aldryn_events/emails/manager_confirmation.subject.txt',
        dictionary=ctx
    )
    body = render_to_string(
        template_name='aldryn_events/emails/manager_confirmation.body.txt',
        dictionary=ctx
    )

    if emails:  # don't try to send if the list is empty
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, emails)


def get_additional_styles():
    """
    Get additional styles choices from settings
    """
    choices = []
    raw = getattr(settings, 'ALDRYN_EVENTS_PLUGIN_STYLES', False)

    if raw:
        if isinstance(raw, basestring):
            raw = raw.split(',')
        for choice in raw:
            try:
                # Happened on aldryn to choice be a tuple with two
                # empty strings and this break the deployment. To avoid that
                # kind of issue if something fais we just ignore.
                clean = choice.strip()
                choices.append((clean.lower(), clean.title()))
            except Exception:
                pass
    return choices


def get_monthdates(month, year):
    # 0: Monday, 6: Sunday (not using isoweekdays)
    firstweekday = getattr(settings, 'ALDRYN_EVENTS_CALENDAR_FIRST_WEEKDAY', 0)
    cal = calendar.Calendar(firstweekday)
    return cal.itermonthdates(year, month)


def build_calendar(year, month, language, namespace=None):
    """
    Returns complete list of monthdates with events happening in that day
    """
    from .models import Event
    month = int(month)
    year = int(year)

    # Get a list of all dates in this month (with pre/succeeding for nice
    # layout)
    monthdates = [(x, []) for x in get_monthdates(month, year)]
    if len(monthdates) < 6 * 7:
        # always display six weeks to keep the table layout consistent
        if month == 12:
            month = 0
            year += 1

        next_month = [(x, []) for x in get_monthdates(month + 1, year)]
        if next_month[0][0].month == month + 1:
            monthdates += next_month[:7]
        else:
            monthdates += next_month[7:14]

    # get all upcoming events, ordered by start_date
    filter_args = (
        Q(start_date__gte=monthdates[0][0],
          start_date__lte=monthdates[-1][0]) |
        Q(
            Q(end_date__isnull=True) | Q(
                end_date__gte=monthdates[0][0],
                end_date__lte=monthdates[-1][0]
            ),
            start_date__lte=monthdates[0][0]
        )
    )
    events = (Event.objects.namespace(namespace)
              .published()
              .active_translations(language)
              .language(language)
              .filter(filter_args)
              .order_by('start_date'))

    # merge events into monthdates, but do the grouping manually
    # because need to consider all event duration, not only start date
    monthdates = SortedDict(monthdates)

    def get_event_dates(obj):
        return [obj.start_date + timedelta(days=i) for i in range(obj.days)]

    for event in events:
        for day in get_event_dates(event):
            if day in monthdates:
                monthdates[day].append(event)

    return monthdates


def date_or_datetime(d, t):
    # either a date or a datetime
    if d and t:
        # TODO: not timezone aware!
        return datetime(d.year, d.month, d.day, t.hour, t.minute)
    elif d:
        return d
    else:
        return None


def namespace_is_apphooked(namespace):
    """
    Check if provided namespace has an app-hooked page.
    Returns True or False.
    """
    try:
        reverse('{0}:events_list'.format(namespace))
    except (NoReverseMatch, AttributeError):
        return False
    return True
