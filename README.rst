.. contents::

Introduction
============

.. image:: https://secure.travis-ci.org/collective/collective.listingviews.png
    :target: http://travis-ci.org/collective/collective.listingviews

``collective.listingviews`` allows a Plone site administrator to quickly create a new display
view their content types, folders, collections and eea.facetednavigation. It will also let you create
custom portlets and mosaic tiles. Compatible with Plone 4.1-5.2.

- you will not have to deploy a new plugin, unlike creating your own views in python and Page Templates
- you will not have to learn Page Templates, unlike ambidexterity or collective.themefragments
- your views will appear in the display menu, unlike ambidexterity or collective.themefragments
- you can have as many alternative views as you want for a given content type, unlike ambidexterity

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
3. Once you've added your view definition you can use the lising view in the following
   - "Display Menu" on a folder - displays both folder fields + contents fields
   - "Display Menu" on a collection - display both collection fields + collected item fields
   - "Display Menu" on a Page or other content type to display that items fields - displays just the item fields
   - "Listing view portlet" pointing to a target collection or folder or item
   - "Listing view portlet" to show fields and/or lists of the current context
   - Standard tiles "Content Listing Tile". Select your view from the "listing view" list
   |display menu|
   |unthemed| 
4. If you require further customisation: use diazo to customise the layout/html of your fields or you can
   use custom fields via "Site setup" if you need combined field values, to format a value or access plone api's.
   |themed|
5. For non-default metadata you can use the "Custom Fields" control panel to add additional calculated fields
   that be view used in any of your listing views.


For example you could

- create a news listing which displays the first sentence and publish date of each news item and lead image
- create a footer portlet for each page which displays the last updated date of the current content
- create a portlet which grabs a random image from a folder
- folder listing of downloads with size and mimetype icon

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

Plone 4.3.5/4.3.6 issues
========================

There is a known issue which breaks widgets when editing listing views.
This is due to a regression bug in z3c.form 3.2.3 which ships with Plone 4.3.5 and 4.3.6.

You will need to pin a different version of z3c.form. Add the following to versions::

    [versions]
    ...
    z3c.form = 3.2.4

(If for some reason you need to pin an older version of z3c.form you should be fine.
Just stay away from the 3.2.3 version)

Worked Examples
===============

See the `doctests for a worked example <https://github.com/collective/collective.listingviews/blob/master/src/collective/listingviews/tests/listingviews.rst/>`_.


Contributing
============

Development is at http://github.com/collective/collective.listingviews

Initial development was funded by `PretaWeb`_.

We have some ideas on where this could go:

- Mimetype icon
- moments support for relative dates
- Support storing configuration in YAML inside the theme instead of plone.app.registry.
- Allow a custom field to be a formatter that can be applied to other fields. ie takes a value
  and turns it into a different value such as an image url to a url tag, or a date to a localised date.
- Pre-calculate custom fields, i.e. add them to catalog metadata.
- Support table base html template for more useful listings without diazo
- Support tags as links to site search
- Safe HTML filtering for all fields. Currently not implemented.
- Export as a theme fragment for more advanded listings.
- Debug custom fields. Allow selection of content to test fields quickly.
- Migration of views. Provide a way to make bulk changes in content from one
  listingview to another listingview. This would allow a new "template" to
  be created and tested and then switched in production.
- Support customisation of batching settings.
- Support grouping (or you can use collective.fieldcollapsing)
- Support hierarchical listing. Allow navigation portlets, sitemaps with
  additional fields. Maybe different kind of views?  Maybe allow views to be
  used as fields within other views?
- Support AJAX batching and infinite lists (auto-load next when scrolled
  down).

.. _plone.app.contentlistingtile: https://github.com/plone/plone.app.contentlistingtile
.. _plone.app.collection: https://github.com/plone/plone.app.collection
.. _PretaWeb: http://www.pretaweb.com
.. _TAL expressions: http://developer.plone.org/functionality/expressions.html
