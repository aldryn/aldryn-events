#####################
Using Aldryn Events
#####################

.. note::
   This part of the guide assumes that django CMS has been :doc:`appropriately installed and
   configured </introduction/installation>`, including Aldryn Events, and that :doc:`an Events page
   has been set up </introduction/basic_usage>`.


************
Add an event
************

Visit the Events page. You should see that the django CMS toolbar now contains a new item, *Events*. Select *Add Event...* from this menu.

Provide some basic details, such as:

* the ``Short description`` is a brief summary of the Event, that will be used in lists of Events
* an event must have a ``Start date``, but the other date/time fields are optional
* for the ``Location``, enter as complete address as possible - Aldryn Events will pass this on to
  Google Maps to display a map, so it needs to be unambiguous and accurate

and **Save** your event.

It now exists in the database and will be listed on the Events page. Notice that the calendar also
indicates that something's on.

You can use the standard django CMS placeholder interface to add more content to your event.

Advanced settings
=================

An event's *Advanced* settings include:

* precise ``Location latitude``/``Location longitude`` (this overrides the geolocation based on the
  ``Location`` field)
* Event registration, that allows you to collect data from prospective attendees - their replies
  are stored in the database (see *Aldryn Events > Registrations* in the Admin.)
* Event co-ordinators, who will receive the registration messages
* an external registration link - for example, if you're using a service such as `Tito
  <http://ti.to>`_

*******
Plugins
*******

The Events page is the easy way in to events on the system, but Aldryn Events also includes a
number of plugins that can be inserted into any django CMS page - indeed, into any content - to
deliver information about events.

For example, if you have a news article announcing a series of seminars, you can drop an Events
plugin into that page to insert an automatically-updated list of items.

Calendar
========

A month view, similar to the one that appears on the main Events page.

List
====

Choose the events you wish to have displayed.

Upcoming or past events
=======================

An automatic list of events.
