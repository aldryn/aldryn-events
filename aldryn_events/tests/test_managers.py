# -*- coding: utf-8 -*-
import mock
from django.utils.timezone import get_current_timezone

from datetime import datetime

from .base import EventBaseTestCase


class EventManagerTestCase(EventBaseTestCase):
    """ Tests EventManager and EventQuerySet """

    @mock.patch('aldryn_events.managers.timezone')
    def test_ongoing(self, timezone_mock):
        timezone_mock.now.return_value = datetime(
            2014, 4, 7, 9, 30, tzinfo=get_current_timezone()
        )
        self.fail()
