.. contents::

Introduction
============

``collective.listingviews`` allows a Plone site administrator to create
new views through the web.  They can use this to:

- create custom views of folders or collections that include metadata and
  content from contained or matching items;
- create custom listing portlets with additional information such as
  lead images, publication dates or authors;
- create listing views with subqueries or python via `TAL expressions`_;
- create additional views of content items, showing other aspects of the
  content;
- create portlets to display information about the current item such as last
  updated date;
- use an ItemView type portlet to display a whole item in a portlet;
- create carousel portlets which pull content or images from collections or
  folders and apply javascript to them.

Listing Views are designed to be simple to create quickly on a Plone site
and avoid the complexity of creating custom page templates or overridden
views for many common cases.

View definitions are created inside the Plone Site setup for particular
content types. Content editors can apply the views to content items via the
``Display Menu`` in a ``Listing View Portlet`` (and in the future in a
``Content Listing Tile``).

The HTML markup used by the view is simple and designed to be easily adapted
to your needs using CSS or Diazo. Each view consists of:

- a definition list of fields of the content item;
- a list of definition lists of fields for each the items in the folder, or
  collection items;
- unique CSS classes for the lists and each field type.

By default the fields that make up a ListingView definition can be one of
the following:

- Creation Date (Date, Date & Time)
- Creator
- Description
- Effective Date (Date, Date & Time)
- End Date (Date, Date & Time)
- Expiration Date (Date, Date & Time)
- Short Name (with or without Link)
- Size
- Location
- Modification Date (Date, Date & Time)
- State
- Start Date (Date, Date & Time)
- Tags
- Title (with or without Link)
- Total number of comments
- + any custom TAL expressions

Worked Examples
===============

.. include:: ./tree/master/src/collective/listingviews/tests/listingviews.rst

See the `doctests for a worked example`_

.. _doctests for a worked example: ./src/collective/listingviews/tests/listingviews.rst

Contributing
============

``collective.listingviews`` is an initial attempt to create a Plone plugin
that is flexible yet simple to understand.  To make it even more useful we
need feedback and pull requests to enable it to replace custom Page
Templates in more cases, while keeping it easy to understand.

Development is at http://github.com/collective/collective.listingviews

Initial development was funded by `PretaWeb`_.

We have some ideas on where this could go:

- Safe HTML filtering for all fields. Currently not implemented.
- Support `plone.app.contentlistingtile`_ for Deco or ``collective.cover``.
  ``contentlistingtile`` allows custom views to be selected so this should
  be simple.
- Support `plone.app.collection`_. Currently only old-style collections
  are supported.
- Preview view as ZPT. This provides a way to learn ZPT and a base to start
  from when more complex views are needed.
- Debug custom fields. Allow selection of content to test fields quickly.
- Migration of views. Provide a way to make bulk changes in content from one
  listingview to another listingview. This would allow a new "template" to
  be created and tested and then switched in production.
- Support customisation of batching settings.
- Allow GET requests so that the list can act as a custom search listing
  page.
- Support grouping.
- Support hierarchical listing. Allow navigation portlets, sitemaps with
  additional fields. Maybe different kind of views?  Maybe allow views to be
  used as fields within other views?
- Support AJAX batching and infinite lists (auto-load next when scrolled
  down).
- Reuse TAL on different fields. The TAL becomes a formatter function
  instead of a field; e.g. convert date or turn Title into link.  Functions
  let you select with fields they apply to, or apply to whole item (i.e.
  custom field).
- Pre-calculate custom fields, i.e. add them to catalog metadata.

.. _plone.app.contentlistingtile: https://github.com/plone/plone.app.contentlistingtile
.. _plone.app.collection: https://github.com/plone/plone.app.collection
.. _PretaWeb: http://www.pretaweb.com
