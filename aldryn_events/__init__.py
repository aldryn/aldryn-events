# -*- coding: utf-8 -*-

__version__ = '1.1.1'

default_app_config = 'aldryn_events.apps.AldrynEvents'

# TODO: See if this can now be removed.
request_events_event_identifier = 'aldryn_events_current_event'

ORDERING_FIELDS = (
    'start_date', 'start_time', 'end_date', 'end_time', 'pk'
)

ARCHIVE_ORDERING_FIELDS = (
    '-start_date', '-start_time', 'end_date', 'end_time', 'pk'
)
