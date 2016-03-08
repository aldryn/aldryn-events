# -*- coding: utf-8 -*-
import datetime
import calendar

from cms.utils.i18n import force_language, get_language_object
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
try:
    from collections import OrderedDict
except ImportError:
    # Python < 2.7
    from django.utils.datastructures import SortedDict as OrderedDict
from django.conf import settings


def build_months(year, is_archive_view=False):
    months = OrderedDict()
    month_numbers = range(1, 12 + 1)

    if is_archive_view:
        month_numbers = list(reversed(month_numbers))

    for month in month_numbers:
        months[month] = {
            'year': year,
            'month': month,
            'date': datetime.date(year, month, 1),
            'events': []
        }
    return months


def group_events_by_year(events):
    """
    Given a queryset of event objects,
    returns a sorted dictionary mapping years to event objects.
    """
    years = OrderedDict()

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

    events_by_year = OrderedDict()
    for event in events:
        year = event.start_date.year
        if year not in events_by_year:
            events_by_year[year] = {
                'year': year,
                'date': datetime.date(year, 1, 1),
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
    ).strip()
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
    ).strip()
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


def update_monthdates(monthdates, event, first_date, last_date):
    """
    Updates monthdates events in place. Returns monthdates.
    :param monthdates: OrderedDict to update
    :param event: Event that should be processed
    :param first_date: first date of monthdates
    :param last_date: last date of monthdates
    :return: OrderedDict, link to monthdates (updated in place!)
    """
    day = max(event.start_date, first_date)
    end_date = day if event.end_date is None else event.end_date
    while day <= end_date and day <= last_date:
        monthdates[day].append(event)
        day += datetime.timedelta(days=1)
    return monthdates


def get_event_q_filters(first_date, last_date):
    """
    Returns tuple of filters applicable to event QuerySet for filtering events
    that are happening/visible in between first_date (included) and
    last_date (included).
    :param first_date: datetime.date object, first date for range
    :param last_date: datetime.date object, last date for range
    :return: tuple of Q objects for .filter() method
    """
    q_start_in_month_dates = Q(start_date__gte=first_date,
                               start_date__lte=last_date)
    q_end_in_month_dates = Q(end_date__gte=first_date,
                             end_date__lte=last_date)
    q_end_is_greater = Q(end_date__gt=last_date)
    # actual filter arguments
    filter_args = (
        q_start_in_month_dates |
        Q(q_end_in_month_dates | q_end_is_greater,
          start_date__lte=first_date))
    return filter_args


def build_calendar(year, month, language, namespace=None, site_id=None):
    """
    Returns complete list of monthdates with events happening in that day
    """
    from .models import Event
    month = int(month)
    year = int(year)

    # Get a list of all dates in this month (with pre/succeeding for nice
    # layout)
    monthdates = list(get_monthdates(month, year))
    if len(monthdates) < 6 * 7:
        # always display six weeks to keep the table layout consistent
        if month == 12:
            month = 0
            year += 1

        next_month = list(get_monthdates(month + 1, year))
        if next_month[0].month == month + 1:
            monthdates += next_month[:7]
        else:
            monthdates += next_month[7:14]

    first_date = monthdates[0]
    last_date = monthdates[-1]
    filter_args = get_event_q_filters(first_date, last_date)
    valid_languages = get_valid_languages(namespace, language, site_id)

    # get all upcoming events, ordered by start_date
    events = (Event.objects.namespace(namespace)
              .published()
              .active_translations(language)
              .language(language)
              .filter(filter_args))
    # use events that can be resolved for this namespace and language
    # with respect to language fallback settings
    events = events.translated(*valid_languages).order_by('start_date')

    events_outside_ongoing = events.filter(
        Q(Q(end_date__isnull=True) | Q(end_date__gt=last_date)),
        start_date__lt=first_date)
    all_dates_events = list(events_outside_ongoing)

    def all_dates_events_copy():
        """Return a copy of events list that should be present on each day"""
        return all_dates_events[:]

    monthdates = OrderedDict((date, all_dates_events_copy())
                             for date in monthdates)

    for event in events.exclude(pk__in=events_outside_ongoing):
        update_monthdates(monthdates, event, first_date, last_date)

    return monthdates


def date_or_datetime(d, t):
    # either a date or a datetime
    if d and t:
        # TODO: not timezone aware!
        return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute)
    elif d:
        return d
    else:
        return None


def is_valid_namespace(namespace):
    """
    Check if provided namespace has an app-hooked page.
    Returns True or False.
    """
    try:
        reverse('{0}:events_list'.format(namespace))
    except (NoReverseMatch, AttributeError):
        return False
    return True


def is_valid_namespace_for_language(namespace, language_code):
    """
    Check if provided namespace has an app-hooked page for given language_code.
    Returns True or False.
    """
    with force_language(language_code):
        return is_valid_namespace(namespace)


def get_valid_languages(namespace, language_code, site_id=None):
        langs = [language_code]
        if site_id is None:
            site_id = getattr(Site.objects.get_current(), 'pk', None)
        current_language = get_language_object(language_code, site_id)
        fallbacks = current_language.get('fallbacks', None)
        if fallbacks:
            langs += list(fallbacks)
        valid_translations = [
            lang_code for lang_code in langs
            if is_valid_namespace_for_language(namespace, lang_code)]
        return valid_translations
