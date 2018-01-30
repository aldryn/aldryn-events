CHANGELOG
=========

2.1.0 (2018-01-30)
------------------

* Added Django 1.11 support


2.0.0 (2018-01-25)
------------------

* Introduced django CMS 3.5 support
* Added Django 1.10 support
* Dropped aldryn-reversion/django-reversion support
* Dropped Django 1.6 and 1.7 support


1.1.7 (2016-11-07)
------------------

* Fixed a unicode error when editing an event in the admin
* Fixed an AttributeError raised from the deprecated CHOICES attribute in
  django-extended-choices


1.1.6 (2016-09-05)
------------------

* Fixed related_name inconsistency with django CMS 3.3.1
* Dropped support for djangoCMS < 3.2
* Introduced support for djangoCMS 3.4.0


1.1.5 (2016-07-14)
------------------

* Fixed an issue where under some circumstances, an earlier migration would fail


1.1.4 (2016-07-07)
------------------

* Updated translations
* Enable configurable plugin caching for CMS 3.3.0+ installations
* Disable spelling test until sphinxcontrib-spelling is updated


1.1.3 (2016-05-26)
------------------

* Changed form field width in admin
* Updated tests to include Python 3.5, Django 1.9 and CMS 3.3 combinations
* Improved documentation regarding appconfig during upgrades.


1.1.2 (2016-05-24)
------------------

* Add support for Python 3.5


1.1.0 (2016-03-10)
------------------

* Add stripped default django templates to `/aldryn_events/templates`
* Remove unused render_placeholder configs
* Add static_placeholders where necessary
* Simplify templates


1.0.12 (2016-03-03)
-------------------

* install django-tablib by default, since a Django 1.8 and 1.9 compatible
  version is now available on pypi. Fixes circular import issues with previous
  conditional setup of tablib on aldryn.


1.0.11 (2016-02-17)
-------------------

* don't install django_tablib if it is not installed (aldryn)
* pretty name in admin ("Aldryn Events" instead of "Aldryn_events")


1.0.10 (2016-02-16)
-------------------

* Allow blank app_title
* Create default app_config in migrations


1.0.9 (2016-02-11)
------------------

* Add Django 1.9 compatibility
* Clean up test environments


1.0.8 (2016-01-12)
------------------

* Improves compatibility with recent versions of django-reversion
* Adds integration tests against CMS v3.2.x


1.0.7 (2015-01-09)
------------------

* Cleaned-up test configuration
* Adds revision-support to wizards


1.0.6 (2015-11-12)
------------------

* Use aldryn-translation-tools >=0.2.1
* Wizard for CMS 3.2


1.0.5 (2015-09-09)
------------------

* Fix unicode issue
* Support Django 1.8
* Update test matrix
* Fix Django migration issue
* Enhanced integration tests
* Make CMS menu more resilient
* Use Translations Tools 0.1.2


1.0.4 (2015-08-04)
------------------

* Make CMSAttachMenu usage optional
* CMSAttachMenu respects published flag
* Add "latest first" flag on apphook for reversing the natural order of events
* Enhance Events list view for easier apphook assignment
* Enhance the CMSToolbar for consistency and ease-of-use


1.0.3 (2015-07-28)
------------------

* Allows operation on versions of Django with non-standard version numbers.
* Adds more configuration for frontend testing.


1.0.2 (2015-07-22)
------------------

* Unrestricts Aldryn Translation Tools version.
* Implements AllTranslationsMixin where appropriate.


1.0.1 (2015-07-22)
------------------

* Adds automated frontend tests and configuration
* Pin some dependencies to current, known versions


1.0.0 (2015-07-08)
------------------

* Initial public release


0.8.10 (2015-06-11)
-------------------

* get_absolute_url now recognize language settings
* search index now correctly recognize thread language
  new requirement: aldryn-translation-tools
* added events cms menu
* added initial docs structure
* added support for fallbacks


0.8.4 (2015-03-21)
------------------

* multi-boilerplate support
  new requirement: aldryn-boilerplates (needs configuration)


0.7.5 (2014-05-23)
------------------

* fixes bug with timezones
* fixes bug with events without end_date not being displayed in list view


0.3.0 (2013-04-26)
------------------

* changed the description field from HTMLField to Placeholderfield. A data migration
  transforms the html into a text plugin.
* switched the HTMLField of short_description from tinymce to ckeditor
* added a "location" text field


0.2.18 (2013-04-11)
-------------------

* registration: larger address field, company, mobile number
* slightly prettier registration form
* bugfixes


0.2.16 (2013-03-21)
-------------------

* bugfixes
* configurable notifications for managers and user at event registration


0.2.14 (2013-02-20)
-------------------

* added optional archive navigation and views
* more translations


0.2.12 - 0.2.13 (2013-02-04)
----------------------------

* some german translations
* optionally allow hiding months in navigation that don't have events


0.2.0 - 0.2.11
--------------

* lots of stuff


0.2.0 (2012-11-27)
------------------

* initial internal release
