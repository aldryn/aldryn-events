from unittest import TestCase

from django.core import mail
from django.core.mail import send_mail
from django.conf import settings
from django.test import TestCase

from cms import api
from cms.utils import get_cms_setting

from .cms_plugins import EventListCMSPlugin
from .models import Event, EventCoordinator


class EventAddTest(TestCase):
    su_username = 'user'
    su_password = 'pass'

    def setUp(self):
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.page = api.create_page('page', self.template, self.language, published=True)
        self.placeholder = self.page.placeholders.all()[0]
        self.event = Event.objects.create(title='Event2014', start_date='2014-09-10', slug='open-air')

    def test_create_event(self):
        """
        We can create an event with a name
        """
        title = 'Concert'
        before_count = Event.objects.count()
        Event.objects.create(title=title, start_date=self.event.start_date, slug='open-concert')
        after_count = Event.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_add_event_app(self):
        """
        We add an event to the app
        """
        self.page.application_urls = 'EventListAppHook'
        self.page.publish(self.language)
        event = Event.objects.create(title=self.event.title, location='Luzern', start_date=self.event.start_date,
                                     slug='open-event')
        url = event.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, event.title)

    def test_add_location_to_event(self):
        """
        We create a coordinator and add him to the created event
        """
        loc = 'Basel'
        title = 'Greenfield'
        event = Event.objects.create(title=title, location=loc,  start_date=self.event.start_date, slug='open-green')
        self.assertEqual(loc, event.location)

    def test_add_event_plugin_api(self):
        """
        We add an event to the Event Plugin and look it up
        """
        title = 'Newone'
        event = Event.objects.create(title=title, start_date=self.event.start_date, slug='open-new')
        plugin = api.add_plugin(self.placeholder, EventListCMSPlugin, self.language)
        plugin.events.add(event)
        plugin.save()
        self.page.publish(self.language)
        url = event.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, event.title)

    def test_delete_event(self):
        """
        We can delete an event
        """
        title = 'Delete Event'
        Event.objects.create(title=title, start_date=self.event.start_date, slug='open-delete')
        Event.objects.translated(title='Delete Event').delete()
        self.assertFalse(Event.objects.translated(title='Delete Event'))

    def test_email_to_coordinator_event(self):
        """
        We can send an email to the coordinator
        """
        title = 'St.Galle'
        event = Event.objects.create(title=title,  start_date=self.event.start_date, slug='open-email')
        name = 'Carl'
        email = 'bla@bla.bla'
        coord = EventCoordinator.objects.create(name=name, email=email)
        coord.event = event
        coord.save()
        send_mail('Subject here', 'Here is the content of the mail.', 'from@test.com', [coord.email],
                  fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')
