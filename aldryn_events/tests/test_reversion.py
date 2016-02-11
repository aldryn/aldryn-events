# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
import six

from django.db import transaction
try:
    from reversion.revisions import create_revision, get_for_object
except ImportError:
    from reversion import create_revision, get_for_object

from cms import api
from cms.utils.i18n import force_language
from aldryn_events.models import Event
from aldryn_reversion.core import create_revision as aldryn_create_revision

from parler.utils.context import switch_language

from .base import EventBaseTestCase, tz_datetime


class ReversionTestCase(EventBaseTestCase):
    def setUp(self):
        super(ReversionTestCase, self).setUp()
        self.create_base_pages()
        self.default_en = {
            'title': 'Event2014',
            'slug': 'open-air',
            'start_date': tz_datetime(2014, 9, 10),
            'publish_at': tz_datetime(2014, 9, 10, 9),
            'app_config': self.app_config
        }
        self.default_de = {
            'title': 'Ereignis',
            'slug': 'im-freien'
        }
        self.default_content = {
            'en': 'Default english content',
            'de': 'default german content'
        }

    def create_event_revision(self, obj, content=None, **kwargs):
        with transaction.atomic():
            with create_revision():
                # populate event with new values
                for property, value in six.iteritems(kwargs):
                    setattr(obj, property, value)
                if content:
                    # get correct plugin for language. do not update the same
                    # one.
                    language = obj.get_current_language()
                    plugins = obj.description.get_plugins().filter(
                        language=language)
                    plugin = plugins[0].get_plugin_instance()[0]
                    plugin.body = content
                    plugin.save()
                obj.save()

    def revert_to(self, object_with_revision, revision_number):
        """
        Revert <object with revision> to revision number.
        """
        # get by position, since reversion_id is not reliable,
        version = list(reversed(
            get_for_object(
                object_with_revision)))[revision_number - 1]
        version.revision.revert()

    def create_default_event(self, translated=False):

        event = Event.objects.create(**self.default_en)
        with switch_language(event, 'en'):
            api.add_plugin(event.description, 'TextPlugin', 'en',
                           body=self.default_content['en'])

        # check if we need a translated event
        if translated:
            event.create_translation('de', **self.default_de)
            with switch_language(event, 'de'):
                api.add_plugin(event.description, 'TextPlugin', 'de',
                               body=self.default_content['de'])

        return Event.objects.language('en').get(pk=event.pk)

    def make_new_values(self, values_dict, replace_with):
        """
        Replace formating symbol {0} with replace_with param. modifies dates by
        + timedelta(days=int(replace_with)) Returns new dictionnary with same
        keys and replaced symbols.
        """
        new_dict = {}
        for key, value in values_dict.items():
            if key in ('start_date', 'end_date'):
                new_val = value + timedelta(days=replace_with)
                if type(new_val) != datetime.date:
                    new_val = new_val.date()
            elif key in ('start_time', 'end_time'):
                new_val = value + timedelta(hours=replace_with)
            elif key in ('publish_at',):
                new_val = value + timedelta(days=replace_with)
            else:
                new_val = value.format(replace_with)
            new_dict[key] = new_val
        return new_dict

    def test_revert_revision(self):
        values_raw = {
            'title': 'Title revision {0}',
            'slug': 'revision-{0}-slug',
            'start_date': tz_datetime(2014, 9, 10),
            'publish_at': tz_datetime(2014, 9, 10),
        }

        content1 = 'Revision 1 content'
        content2 = 'Revision 2 content, brand new one!'

        event = self.create_default_event()
        # revision 1
        revision_1_values = self.make_new_values(values_raw, 1)
        event.set_current_language('en')
        self.create_event_revision(event, content=content1,
                                   **revision_1_values)
        # revision 2
        revision_2_values = self.make_new_values(values_raw, 2)

        event = Event.objects.get(pk=event.pk)
        event.set_current_language('en')
        self.create_event_revision(event, content=content2,
                                   **revision_2_values)

        # check that latest revision values are used
        with switch_language(event, 'en'):
            url_revision_2 = event.get_absolute_url()
        response = self.client.get(url_revision_2)
        self.assertContains(response, revision_2_values['title'])
        self.assertContains(response, content2)
        # test that there is no default values
        self.assertNotContains(response, self.default_content['en'])
        self.assertNotContains(response, self.default_en['title'])
        # test that there is no previous version content (placeholder)
        self.assertNotContains(response, content1)

        # test revert for event
        self.revert_to(event, 1)
        # test urls, since slug was changed they shouldn't be the same.
        event = Event.objects.get(pk=event.pk)
        with switch_language(event, 'en'):
            url_revision_1 = event.get_absolute_url()
        self.assertNotEqual(url_revision_2, url_revision_1)

        response = self.client.get(url_revision_1)

        self.assertContains(response, revision_1_values['title'])
        self.assertContains(response, content1)

        # test that there is no default content
        self.assertNotContains(response, self.default_content['en'])
        self.assertNotContains(response, self.default_en['title'])

        # test that there is no revision 2 content
        self.assertNotContains(response, revision_2_values['title'])
        # test that there is no revision 2 content (placeholder)
        self.assertNotContains(response, content2)

    def test_revert_revision_with_translation(self):
        # does not covers image translated FK field
        values_raw_en = {
            'title': 'Title revision {0} en',
            'slug': 'revision-{0}-slug-en',
            'short_description': 'revision {0} short description en'
        }

        values_raw_de = {
            'title': 'Title revision {0} de',
            'slug': 'revision-{0}-slug-de',
            'short_description': 'revision {0} short description de'
        }

        content1_en = 'Revision 1 content'
        content2_en = 'Revision 2 content, brand new one!'

        content1_de = 'Revision German 1 content'
        content2_de = 'Revision German 2 content, brand new one!'

        event = self.create_default_event(translated=True)

        # prepare default urls to compare.
        with switch_language(event, 'en'):
            default_event_url_en = event.get_absolute_url()
        with switch_language(event, 'en'):
            default_event_url_de = event.get_absolute_url()

        # revision 1 en
        revision_1_values_en = self.make_new_values(values_raw_en, 1)
        revision_1_values_de = self.make_new_values(values_raw_de, 1)
        event.set_current_language('en')
        self.create_event_revision(event, content=content1_en,
                                   **revision_1_values_en)
        # revision 2 de
        event = Event.objects.get(pk=event.pk)
        event.set_current_language('de')
        self.create_event_revision(event, content=content1_de,
                                   **revision_1_values_de)

        # test latest revision with respect to languages
        with switch_language(event, 'en'):
            revision_1_url_en = event.get_absolute_url()
            response = self.client.get(revision_1_url_en)

            self.assertContains(response, revision_1_values_en['title'])
            self.assertContains(response,
                                revision_1_values_en['short_description'])
            self.assertNotEqual(revision_1_url_en, default_event_url_en)
            self.assertNotEqual(revision_1_url_en, default_event_url_de)

        with switch_language(event, 'de'):
            revision_1_url_de = event.get_absolute_url()
            response = self.client.get(revision_1_url_de)

            self.assertContains(response, revision_1_values_de['title'])
            self.assertContains(response,
                                revision_1_values_de['short_description'])
            # test against the default urls
            self.assertNotEqual(revision_1_url_de, default_event_url_en)
            self.assertNotEqual(revision_1_url_de, default_event_url_de)
            # test against the other translation
            self.assertNotEqual(revision_1_url_de, revision_1_url_en)

        # revision 2a (3) change only german translation
        revision_2_values_de = self.make_new_values(values_raw_de, 2)
        event = Event.objects.get(pk=event.pk)
        event.set_current_language('de')
        self.create_event_revision(event, content=content2_de,
                                   **revision_2_values_de)

        event = Event.objects.get(pk=event.pk)
        # test latest (rev 2a atm) revision with respect to languages
        with switch_language(event, 'en'):
            revision_2_url_en = event.get_absolute_url()
            response = self.client.get(revision_2_url_en)

            self.assertContains(response, revision_1_values_en['title'])
            self.assertContains(response,
                                revision_1_values_en['short_description'])
            self.assertContains(response, content1_en)

            # test that en version in last revision doesn't contains german
            # content (placeholder)
            self.assertNotContains(response, content1_de)
            self.assertNotContains(response, content2_de)

            # compare with default (initial) urls.
            self.assertNotEqual(revision_2_url_en, default_event_url_en)
            self.assertNotEqual(revision_2_url_en, default_event_url_de)

            # check that url was not changed.
            self.assertEqual(revision_2_url_en, revision_1_url_en)

        with switch_language(event, 'de'):
            revision_2_url_de = event.get_absolute_url()
            response = self.client.get(revision_2_url_de)

            self.assertContains(response, revision_2_values_de['title'])
            self.assertContains(response,
                                revision_2_values_de['short_description'])
            self.assertContains(response, content2_de)
            # test that other translation content is not being served using
            # revision_1_values_en since it is the only existing English values
            # so far
            self.assertNotContains(response, revision_1_values_en['title'])
            self.assertNotContains(response,
                                   revision_1_values_en['short_description'])
            self.assertNotContains(response, content1_en)

            # test that it doesnt contains previous revision data
            self.assertNotContains(response, revision_1_values_de['title'])
            self.assertNotContains(response,
                                   revision_1_values_de['short_description'])
            self.assertNotContains(response, content1_de)

            # test against the default urls
            self.assertNotEqual(revision_2_url_de, default_event_url_en)
            self.assertNotEqual(revision_2_url_de, default_event_url_de)
            # test against previous revision
            self.assertNotEqual(revision_2_url_de, revision_1_url_de)
            # test against the other translation
            self.assertNotEqual(revision_2_url_de, revision_2_url_en)

        # revision 2b (4) english translation update
        revision_2_values_en = self.make_new_values(values_raw_en, 2)
        event = Event.objects.get(pk=event.pk)
        event.set_current_language('en')
        self.create_event_revision(event, content=content2_en,
                                   **revision_2_values_en)

        event = Event.objects.get(pk=event.pk)
        # test latest (rev 2b atm) revision with respect to languages
        with switch_language(event, 'en'):
            revision_2b_url_en = event.get_absolute_url()
            response = self.client.get(revision_2b_url_en)
            # test latest rev content
            self.assertContains(response, revision_2_values_en['title'])
            self.assertContains(response,
                                revision_2_values_en['short_description'])
            self.assertContains(response, content2_en)

            # test that there is no prev version content
            self.assertNotContains(response, content1_en)

            # test that en version in last revision doesn't contains german
            # content (placeholder)
            self.assertNotContains(response, content1_de)
            self.assertNotContains(response, content2_de)

            # compare with default (initial) urls.
            self.assertNotEqual(revision_2b_url_en, default_event_url_en)
            self.assertNotEqual(revision_2b_url_en, default_event_url_de)

            # check that url was changed.
            self.assertNotEqual(revision_2b_url_en, revision_1_url_en)
            # FIXME: not sure if we need to check against other revision url,
            # even though that translation wasn't changed
            # test against german translation url (previously built)
            # self.assertNotEqual(revision_2b_url_en, revision_2_url_de)

        with switch_language(event, 'de'):
            revision_2b_url_de = event.get_absolute_url()
            response = self.client.get(revision_2b_url_de)

            self.assertContains(response, revision_2_values_de['title'])
            self.assertContains(response,
                                revision_2_values_de['short_description'])
            self.assertContains(response, content2_de)
            # test that other translation content is not being served
            # previous en revision
            self.assertNotContains(response, revision_1_values_en['title'])
            self.assertNotContains(response,
                                   revision_1_values_en['short_description'])
            self.assertNotContains(response, content1_en)
            # latest en revision
            self.assertNotContains(response, revision_2_values_en['title'])
            self.assertNotContains(response,
                                   revision_2_values_en['short_description'])
            self.assertNotContains(response, content2_en)

            # test that it doesnt contains previous revision data
            self.assertNotContains(response, revision_1_values_de['title'])
            self.assertNotContains(response,
                                   revision_1_values_de['short_description'])
            self.assertNotContains(response, content1_de)

            # test against the default urls
            self.assertNotEqual(revision_2b_url_de, default_event_url_en)
            self.assertNotEqual(revision_2b_url_de, default_event_url_de)
            # test against previous revision
            self.assertNotEqual(revision_2b_url_de, revision_1_url_de)
            # test against the other translation
            # previous revision en url
            self.assertNotEqual(revision_2b_url_de, revision_2_url_en)
            # latest revision en url
            self.assertNotEqual(revision_2b_url_de, revision_2b_url_en)

            # test that de url is not changed in new revision
            self.assertEqual(revision_2b_url_de, revision_2_url_de)

        # finaly the revert part.
        # rever to 1, EN=1 DE=1
        self.revert_to(event, 2)
        # get latest state instead of in memory
        event = Event.objects.get(pk=event.pk)
        with switch_language(event, 'en'):
            revision_1_reverted_url_en = event.get_absolute_url()
            response = self.client.get(revision_1_reverted_url_en)

            self.assertContains(response, revision_1_values_en['title'])
            self.assertContains(response,
                                revision_1_values_en['short_description'])
            self.assertNotEqual(revision_1_reverted_url_en,
                                default_event_url_en)
            self.assertNotEqual(revision_1_reverted_url_en,
                                default_event_url_de)

            # test that it is the same.
            self.assertEqual(revision_1_reverted_url_en, revision_1_url_en)

        with switch_language(event, 'de'):
            revision_1_reverted_url_de = event.get_absolute_url()
            response = self.client.get(revision_1_reverted_url_de)

            self.assertContains(response, revision_1_values_de['title'])
            self.assertContains(response,
                                revision_1_values_de['short_description'])
            # test against the default urls
            self.assertNotEqual(revision_1_reverted_url_de,
                                default_event_url_en)
            self.assertNotEqual(revision_1_reverted_url_de,
                                default_event_url_de)
            # test against the other translation
            self.assertNotEqual(revision_1_reverted_url_de, revision_1_url_en)
            self.assertEqual(revision_1_reverted_url_de, revision_1_url_de)

        # revert to 3, EN=1 DE=2
        self.revert_to(event, 3)
        # test latest (rev 2a atm) revision with respect to languages
        event = Event.objects.get(pk=event.pk)
        with switch_language(event, 'en'):
            revision_2_reversed_url_en = event.get_absolute_url()
            response = self.client.get(revision_2_reversed_url_en)

            self.assertContains(response, revision_1_values_en['title'])
            self.assertContains(response,
                                revision_1_values_en['short_description'])
            self.assertContains(response, content1_en)

            # test that en version in last revision doesn't contains german
            # content (placeholder)
            self.assertNotContains(response, content1_de)
            self.assertNotContains(response, content2_de)

            # compare with default (initial) urls.
            self.assertNotEqual(revision_2_reversed_url_en,
                                default_event_url_en)
            self.assertNotEqual(revision_2_reversed_url_en,
                                default_event_url_de)

            # check that url was not changed.
            self.assertEqual(revision_2_reversed_url_en, revision_2_url_en)

            # plugin and revision related
            self.assertNotContains(response, content2_en)

        with switch_language(event, 'de'):
            revision_2_reversed_url_de = event.get_absolute_url()
            response = self.client.get(revision_2_reversed_url_de)

            self.assertContains(response, revision_2_values_de['title'])
            self.assertContains(response,
                                revision_2_values_de['short_description'])
            self.assertContains(response, content2_de)
            # test that other translation content is not being served using
            # revision_1_values_en since it is the only existing English values
            # so far
            self.assertNotContains(response, revision_1_values_en['title'])
            self.assertNotContains(response,
                                   revision_1_values_en['short_description'])
            self.assertNotContains(response, content1_en)

            # test that it doesnt contains previous revision data
            self.assertNotContains(response, revision_1_values_de['title'])
            self.assertNotContains(response,
                                   revision_1_values_de['short_description'])
            self.assertNotContains(response, content1_de)

            # test against the default urls
            self.assertNotEqual(
                revision_2_reversed_url_de, default_event_url_en)
            self.assertNotEqual(
                revision_2_reversed_url_de, default_event_url_de)
            # test against previous revision
            self.assertNotEqual(revision_2_reversed_url_de, revision_1_url_de)
            # test against the other translation
            self.assertNotEqual(revision_2_reversed_url_de, revision_2_url_en)

    def test_edit_plugin_directly(self):
        content1 = 'Content 1 text'
        content2 = 'Content 2 text'

        with force_language('en'):
            event = self.create_default_event()
        # revision 1
        self.create_event_revision(event, content1)

        self.assertEqual(len(get_for_object(event)), 1)

        # revision 2
        with transaction.atomic():
            plugins = event.description.get_plugins().filter(
                language=event.get_current_language())
            plugin = plugins[0].get_plugin_instance()[0]
            plugin.body = content2
            plugin.save()
            aldryn_create_revision(event)

        self.assertEqual(len(get_for_object(event)), 2)

        response = self.client.get(event.get_absolute_url())
        self.assertContains(response, content2)
        self.assertNotContains(response, content1)

        self.revert_to(event, 1)
        event = Event.objects.get(pk=event.pk)
        response = self.client.get(event.get_absolute_url())
        self.assertContains(response, content1)
        self.assertNotContains(response, content2)
