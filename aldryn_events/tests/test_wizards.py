# -*- coding: utf-8 -*-
from .base import EventBaseTestCase


class TestEventsWizard(EventBaseTestCase):

    def setUp(self):
        super(TestEventsWizard, self).setUp()
        self.super_user_password = 'super_pw'
        self.super_user = self.create_super_user(
            'super', self.super_user_password)
        self.client.login(
            username=self.super_user.username,
            password=self.super_user_password,
        )

    def test_event_opening_wizard(self):
        # Import here to avoid logic wizard machinery
        from aldryn_events.cms_wizards import CreateEventForm

        self.create_base_pages(multilang=False)

        data = {
            'title': 'Yoga retreat',
            'slug': 'yoga-retreat',
            'short_description': '<p>3 day Yoga retreat.</p>',
            'event_content': '<p>Any experience welcome.</p>',
            'start_date': '2015-01-01',
            'is_published': True,
            'app_config': self.app_config.pk,
        }
        form = CreateEventForm(
            data=data,
            wizard_language='en',
            wizard_user=self.super_user,
        )

        self.assertTrue(form.is_valid())
        event = form.save()

        url = event.get_absolute_url('en')
        response = self.client.get(url)
        self.assertContains(response, data['title'], status_code=200)
        self.assertContains(
            response,
            data['short_description'],
            status_code=200,
        )
        self.assertContains(
            response,
            data['event_content'],
            status_code=200,
        )
