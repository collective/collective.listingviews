.. contents::

Introduction
============

ListingViews allows a site administrator to create new views in Plone Site Setup which they either

- Apply to content items via the ``Display Menu``
- Used in Listing View portlet

The html markup used by the view is simple and designed to be easily converted using CSS or Diazo.

Each view consists of

- A definition list of fields of the content item
- A list of definition lists of fields for each the items in the folder, or collection items
- a unique css class

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

Worked Examples
===============

.. include:: ./collective/listingviews/tests/listingviews.rst

See the `doctests for a worked example`_

.. _doctests for a worked example: ./collective/listingviews/tests/listingviews.rst

possible future directions
==========================
- make a listingview tile for use in deco or collective.cover. Tile would include querystring to replace collection. If you wanted to instead reference a tile elsewhere we might need a referencebrowser widget that lets us pick tiles not just content?
- provide a way to make bulk changes in content from one listingview to another listingview. This would allow a new "template" to be
  created and tested and then switched in production.
- support the concept of functions instead of custom fields. When creating a function you specify which fields it can apply to, or the whole object (which makes
  it a custom field). In the listing view, you can now pick the field with or without that function applied.
- interactive testing with a view in control panel of sample content with your functions applied, or a specifc view.
- provide a way to turn a view into zpt so it can be used in fs code.
- implement safe html filtering
- support customisation of batching settings
- support old style collections
- allow get requests so list can act as a custom search listing page.
- support grouping
- support hierarchical listing
- support ajax batching
- support infinite lists (auto load next when scrolled down)

