.. contents::

Introduction
============

.. image:: https://secure.travis-ci.org/collective/collective.listingviews.png
    :target: http://travis-ci.org/collective/collective.listingviews

``collective.listingviews`` allows a Plone site administrator to quickly create a new display
view their content types, folders, collections and eea.facetnavigation. It will also let you create
custom portlets.

.. |listingviews| image:: https://cloud.githubusercontent.com/assets/41700/5023294/b6f6e9e0-6b27-11e4-8516-2b4a50ef66c5.png
  :width: 50pt  
.. |edit listing view| image:: https://cloud.githubusercontent.com/assets/41700/5023298/bdd25150-6b27-11e4-8be8-010e3c2cc6d0.png
  :scale: 50 %
.. |display menu| image:: https://cloud.githubusercontent.com/assets/41700/5023300/c1546ad4-6b27-11e4-844e-e3d658009731.png
  :scale: 50 %
.. |unthemed| image:: https://cloud.githubusercontent.com/assets/41700/5023303/c5cdc2f4-6b27-11e4-9a0d-e89e5b99b71e.png
  :scale: 50 %
.. |themed|  image:: https://cloud.githubusercontent.com/assets/41700/5023306/c9e2f918-6b27-11e4-86aa-efd49d202ec8.png
  :scale: 50 %


1. Go to Site Setup > Listing Views. |listingviews|
2. Select the fields you want to display and give your view a name and class tag. Pick which content types this view will be 
   available to. 
   |edit listing view|
4. Once you've added your view definition you can use the "Display Menu" or "Listing view portlet" to apply this view where you want. 
   If you use it on a folder or
   collection it display a list items with just the fields you defined. If you use your view on a single item, it will display a list
   with a single set of fields. If you use a portlet, you can either point it to a fixed item, folder or collection, or it will display
   the content of the current context. 
   |display menu| 
   |unthemed| 
5. If you require further customisation: use diazo to customise the layout/html of your fields or you can 
   use custom fields via "Site setup" if you need combine field values, format a value or access plone api's.
   |themed| 
   
For example you could

- create a news listing which displays the first sentance and publish date of each news item
- create a footer portlet for each page which displays the last updated date of the current content
- create a portlet which grabs a random image from a folder
- create a listing of folders which contain pdfs of different languages and display links to each version of the pdf.

This plugin is very flexible and can be used to:

- create custom views of folders or collections that include metadata and
  content from contained or matching items;
- create custom listing portlets with additional information such as
  lead images, publication dates or authors;
- create listing views with subqueries or python via `TAL expressions`_;
- create additional views of non-folderish content items, showing other aspects of the
  content;
- create portlets to display information about the current item such as last
  updated date, or even the whole content replacing plugins like ItemViewPortlet;
- create carousel portlets which pull content or images from collections or
  folders and apply javascript to them, replacing collective.carousel are related
  plugins;
- create custom listings for ``eea.facetednavigation``;

Listing Views are designed to be simple to create quickly on a Plone site
and avoid the complexity of creating custom page templates or overridden
views for many common cases.

View definitions are created inside the Plone Site setup by TTW developers. 
Content editors can apply the views to content items via the
``Display Menu`` for content or in a ``Listing View Portlet`` for portlets 
(and in the future in a ``Content Listing Tile``).

The HTML markup used by the view is simple and designed to be easily adapted
to your needs using CSS or Diazo. Each view consists of:

- a definition list of fields of the target or context content item;
- a list of definition lists of fields for each the listed items if the
  target or context is a folder, or collection;
- unique CSS classes for the lists and each field type.

By default Fields that can make up a ListingView are :

- Any Metadata fields stored in the catalog (e.g. Title, Effective Date)
- Some Metadata fields with formatting applied (e.g. Title (Link), Effective Date (Date & Time))
- Any custom TAL expressions

Worked Examples
===============

See the `doctests for a worked example`_


Contributing
============

Development is at http://github.com/collective/collective.listingviews

Initial development was funded by `PretaWeb`_.

We have some ideas on where this could go:

- Nicer GS import/export. Currently uses plone.app.registry.
- Safe HTML filtering for all fields. Currently not implemented.
- Support `plone.app.contentlistingtile`_ for Deco or ``collective.cover``.
  ``contentlistingtile`` allows custom views to be selected so this should
  be simple.
- Preview/export as ZPT. This provides a way to learn ZPT and a base to start
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
.. _TAL expressions: http://developer.plone.org/functionality/expressions.html
