# -*- coding: utf-8 -*-

__version__ = '1.0.3'

request_events_event_identifier = 'aldryn_events_current_event'

ORDERING_FIELDS = (
    'start_date', 'start_time', 'end_date', 'end_time', 'pk'
)

ARCHIVE_ORDERING_FIELDS = (
    '-start_date', '-start_time', 'end_date', 'end_time', 'pk'
)
