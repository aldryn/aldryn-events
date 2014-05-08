# -*- coding: utf-8 -*-
import datetime
from uuid import uuid4
from cms.utils.i18n import get_current_language

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from cms.models.fields import PlaceholderField
from cms.models import CMSPlugin

from extended_choices import Choices
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from djangocms_common.slugs import unique_slugify
from djangocms_text_ckeditor.fields import HTMLField
from hvad.models import TranslatableModel, TranslationManager, TranslatedFields
from sortedm2m.fields import SortedManyToManyField

from .utils import get_additional_styles
from .conf import settings


STANDARD = 'standard'


class EventManager(TranslationManager):
    def published(self, now=None):
        now = now or timezone.now()
        return self.language(get_current_language()).filter(is_published=True, publish_at__lte=now)

    def upcoming(self, count, now=None):
        now = now or timezone.now()
        return self.future(now=now)[:count]

    def past(self, count, now=None):
        now = now or timezone.now()
        return self.archive(now=now)[:count]

    def future(self, now=None):
        """
        includes all events that are not over yet
        """
        now = now or timezone.now()
        return self.published(now=now).filter(end_at__gte=now).order_by('start_at', 'end_at', 'slug')

    def archive(self, now=None):
        """
        includes all events that have ended
        """
        now = now or timezone.now()
        return self.published(now=now).filter(end_at__lt=now).order_by('-start_at', 'end_at', 'slug')


class Event(TranslatableModel):
    slug = models.SlugField(_('slug'), blank=True, max_length=150, unique=True)

    image = FilerImageField(verbose_name=_('image'), null=True, blank=True, related_name='event_images', on_delete=models.SET_NULL)
    flyer = FilerFileField(verbose_name=_('flyer'), null=True, blank=True, related_name='event_flyers', on_delete=models.SET_NULL)

    start_date = models.DateField(_('start date'))
    start_time = models.TimeField(_('start time'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    end_time = models.TimeField(_('end time'), null=True, blank=True)

    start_at = models.DateTimeField(_('start at'), db_index=True)
    end_at = models.DateTimeField(_('end at'), blank=True)

    is_published = models.BooleanField(_('is published'), default=True,
        help_text=_('wether the event should be displayed'))
    publish_at = models.DateTimeField(_('publish at'), default=timezone.now,
        help_text=_('time at which the event should be published'))

    detail_link = models.URLField(_('external link'), blank=True, default='',
        help_text=('external link to details about this event')
    )

    translations = TranslatedFields(
        title = models.CharField(_('title'), max_length=150, help_text=_('translated')),
        short_description = HTMLField(_('short description'), blank=True, default='', help_text=_('translated')),
        location = models.TextField(_('location'), blank=True, default='')
    )
    description = PlaceholderField('aldryn_events_event_description', verbose_name=_('description'))
    register_link = models.URLField(_('registration link'), blank=True, default='',
        help_text=('link to an external registration system')
    )
    enable_registration = models.BooleanField(_('enable event registration'), default=False)
    registration_deadline_at = models.DateTimeField(_('allow registartion until'), null=True, blank=True, default=None)
    event_coordinators = models.ManyToManyField('EventCoordinator', verbose_name=_('event coordinators'), null=True, blank=True)

    objects = EventManager()

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ('start_at', 'end_at',)

    def __unicode__(self):
        return self.lazy_translation_getter('title', self.pk)

    def clean(self):
        if not self.pk:
            # the translations don't exist yet so we can't access title
            unique_slugify(self, self.slug or uuid4().hex[:8])

        if self.start_date and self.start_time:
            d, t = self.start_date, self.start_time
            self.start_at = datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        elif self.start_date:
            d = self.start_date
            self.start_at = datetime.datetime(d.year, d.month, d.day)

        if self.end_time:
            d, t = self.end_date or self.start_date, self.end_time
            self.end_at = datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        elif self.end_date:
            d = self.end_date
            self.end_at = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
        elif self.start_at:  # because start_at might not be set at validation phase
            self.end_at = self.start_at.replace(hour=23, minute=59, second=59)

        if self.start_at and self.end_at and self.end_at < self.start_at:
            raise ValidationError(_('start should be before end'))

        if self.enable_registration and self.register_link:
            raise ValidationError(_("the registration system can't be active if there is an external registration link. please remove at least one of the two."))

        if self.enable_registration and not self.registration_deadline_at:
            raise ValidationError(_("please select a registration deadline."))

    def start(self):
        # either a date or a datetime
        if self.start_date and self.start_time:
            return self.start_at
        elif self.start_date:
            return self.start_date
        else:
            return None

    def end(self):
        # either a date or a datetime
        if self.end_date and self.end_time:
            return self.end_at
        elif self.end_date:
            return self.end_date
        else:
            return None

    @property
    def is_registration_deadline_passed(self):
        return not (self.registration_deadline_at and self.registration_deadline_at > timezone.now())

    def get_absolute_url(self):
        return reverse('events_detail', kwargs={'slug': self.slug})


class EventCoordinator(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=80, unique=True)

    def __unicode__(self):
        return self.email


class Registration(models.Model):
    SALUTATIONS = Choices(
        ('SALUTATION_FEMALE', 'mrs', _('Frau')),
        ('SALUTATION_MALE', 'mr', _('Herr')),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    language_code = models.CharField(choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0], max_length=32)

    event = models.ForeignKey(Event)
    salutation = models.CharField(_('Anrede'), max_length=5, choices=SALUTATIONS.CHOICES, default=SALUTATIONS.SALUTATION_FEMALE)
    company = models.CharField(_('Company'), max_length=100, blank=True, default='')
    first_name = models.CharField(_('Vorname'), max_length=100)
    last_name = models.CharField(_('Nachname'), max_length=100)

    address_street = models.CharField(_('Adresse'), max_length=100)
    address = models.TextField(_('Adresse'), blank=True, default='')
    address_zip = models.CharField(_('PLZ'), max_length=4)
    address_city = models.CharField(_('Ort'), max_length=100)

    phone = models.CharField(_('Phone number'), blank=True, default='', max_length=20)
    mobile = models.CharField(_('Mobile number'), blank=True, default='', max_length=20)
    email = models.EmailField(_('E-Mail'))

    message = models.TextField(_('Message'), blank=True, default='')


class UpcomingPluginItem(CMSPlugin):
    STYLE_CHOICES = [
        (STANDARD, _('Standard')),
    ]

    style = models.CharField(
        _('Style'), choices=STYLE_CHOICES + get_additional_styles(), default=STANDARD, max_length=50)
    latest_entries = models.PositiveSmallIntegerField(
        _('latest entries'), default=5, help_text=_('The number of latests events to be displayed.'))


class EventListPlugin(CMSPlugin):
    STYLE_CHOICES = [
        (STANDARD, _('Standard')),
    ]

    style = models.CharField(
        _('Style'), choices=STYLE_CHOICES + get_additional_styles(), default=STANDARD, max_length=50)
    events = SortedManyToManyField(Event, blank=True, null=True)

    def __unicode__(self):
        return str(self.pk)

    def copy_relations(self, oldinstance):
        self.events = oldinstance.events.all()