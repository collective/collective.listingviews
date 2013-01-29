.. contents::

Introduction
============

ListingViews allows a site administrator to create new views in Plone Site Setup which they either

- Apply to content items via the ``Display Menu``
- Used in Listing View portlet

Listing Views are designed to be simple to create quickly on a Plone site and avoid the complexity
of creating custom ZPT templates or overridden views for many common cases.
The html markup used by the view is simple and designed to be easily adapted to your needs
using CSS or Diazo.

Each view consists of

- A definition list of fields of the content item
- A list of definition lists of fields for each the items in the folder, or collection items
- Unique css classes for the lists as well as each field type.

Fields that can be selected are

- Metadata fields stored in the catalog (same as can be used on a collection)
- Metadata fields with some built in filters
- Custom TAL expressions

There are many possible uses including

- Create views with custom date formats
- Providing additional views
- Creating new collection portlets with additional fields
- Providing extra fields to additional views using a portlet and diazp
- Preview portlet
- Replacing jbot style overridden ZPT templates with through-the-web equivalent
- creating carousel portlets using folder contents including images via custom image field

Worked Examples
===============

.. include:: ./src/collective/listingviews/tests/listingviews.rst

See the `doctests for a worked example`_

.. _doctests for a worked example: ./src/collective/listingviews/tests/listingviews.rst

Contributing
============

Listing Views is an initial attempt to create a plone plugin that is both flexible yet simple to understand.
To make it even more useful we need feedback and pull requests that make it able to replace more cases
where you might need custom ZPT, while keeping it easy to understand.

Development is at http://github.com/collective/collective.listingviews

Initial development was funded by PretaWeb


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
- Reuse TAL on different fields. TAL becomes filter not field e.g. convert date or turn Title into link.
  When creating a function you specify which fields it can apply to, or the whole object (which makes it a
  it a custom field). In the listing view, you can now pick the field with or without that function applied.

.. _plone.app.contentlistingtile: https://github.com/plone/plone.app.contentlistingtile
.. _plone.app.collection: https://github.com/plone/plone.app.collection
.. _PretaWeb: http://www.pretaweb.com