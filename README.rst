.. contents::

Introduction
============

.. image:: https://secure.travis-ci.org/collective/collective.listingviews.png
    :target: http://travis-ci.org/collective/collective.listingviews

ListingViews allows a Plone site administrator to create views themselves. They can use this to

- Create custom views of folders or collection that include metadata and data from contained items
- Create custom listing portlets with additional information such as lead-images, publication dates or authors.
- Create listing views with subqueries or python via ``TAL expressions``_.
- Create additional views of content items pulling additional data out of the content
- Portlets to display information about the current item such as last updated date
- ItemView type portlet to display a whole item in a portlet.
- Carousel portlets which pull content or images from collections or folders and apply js to them

Listing Views are designed to be simple to create quickly on a Plone site and avoid the complexity
of creating custom ZPT templates or overridden views for many common cases.

View definitions are created inside the Plone Site setup for particular content types. Content editors can apply the views
to content items via the ``Display Menu`` in a ``Listing View Portlet`` (and in the future in a ``Content Listing Tile``).

The html markup used by the view is simple and designed to be easily adapted to your needs
using CSS or Diazo. Each view consists of

- A definition list of fields of the content item
- A list of definition lists of fields for each the items in the folder, or collection items
- Unique css classes for the lists as well as each field type.

By default Fields that can make up a ListingView are :

- Creation Date (Date)
- Creation Date (Date & Time)
- Creator
- Description
- Effective Date (Date)
- Effective Date (Date & Time)
- End Date (Date)
- End Date (Date & Time)
- Expiration Date (Date)
- Expiration Date (Date & Time)
- Short Name
- Short Name (Link)
- Size
- Location
- Modification Date (Date)
- Modification Date (Date & Time)
- State
- Start Date (Date)
- Start Date (Date & Time)
- Tags
- Title
- Title (Link)
- Total number of comments
- + any Custom TAL expressions

Worked Examples
===============

.. include:: ./tree/master/src/collective/listingviews/tests/listingviews.rst

See the `doctests for a worked example`_

.. _doctests for a worked example: ./tree/master/src/collective/listingviews/tests/listingviews.rst

Contributing
============

Listing Views is an initial attempt to create a plone plugin that is both flexible yet simple to understand.
To make it even more useful we need feedback and pull requests that make it able to replace more cases
where you might need custom ZPT, while keeping it easy to understand.

Development is at http://github.com/collective/collective.listingviews

Initial development was funded by ``PretaWeb``_

We have some ideas on where this could go:

- safe html filtering for all fields. Currently not implemented.
- support `plone.app.contentlistingtile`_ for deco or collective.cover. Contentlistingtile allows
  custom views to be selected so this should be simple.
- support `plone.app.collection`_. Currently only old style collections supported.
- preview view as ZPT. Provides way to learn ZPT and base to start when more complex views needed.
- debug custom fields. Allow selection of content to test fields quickly.
- migration of views. provide a way to make bulk changes in content from one listingview to another listingview. This would allow a new "template" to be
  created and tested and then switched in production.
- support customisation of batching settings
- allow get requests so list can act as a custom search listing page.
- support grouping
- support hierarchical listing. Allow navigation portlets, sitemaps with additional fields. Maybe different kind of views?
  Maybe allow views to be used as fields within other views?
- support ajax batching and infinite lists (auto load next when scrolled down)
- Reuse TAL on different fields. TAL becomes formatter function not field e.g. convert date or turn Title into link.
  Functions let you select with fields they apply to, or apply to whole item (ie custom field).
- Pre-calculate custom fields. ie add them to catalog metadata.

.. _plone.app.contentlistingtile: https://github.com/plone/plone.app.contentlistingtile
.. _plone.app.collection: https://github.com/plone/plone.app.collection
.. _PretaWeb: http://www.pretaweb.com