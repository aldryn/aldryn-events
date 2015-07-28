CHANGELOG
=========

1.0.3 (2015-07-28)
------------------

* Allows operation on versions of Django with non-standard version numbers.

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
