###########
Basic usage
###########

Create a django CMS page to hook the Aldryn Events application into. In its *Advanced settings*,
set its ``Application`` to *Events*, and use the provided, default *Events / aldryn_events* in
``Application configurations`` before saving.

.. note::

    If you are upgrading from version 0.7.x or lower, please make sure to visit the page
    *Advanced settings* (as well as every Aldryn Events plugin configuration),
    select application configuration and save it.

The page is now a landing page for events on the site and will show a calendar (empty), which will
be populated as you add events to the system.

The behaviour of the Events system should be largely self-explanatory, but the :doc:`tutorial for
users </user/index>` will guide you through some basic steps if necessary.
