.. contents::

Introduction
============

ListingViews aims to replace the need to override templates for collections, folders, collection porlets or content
views in many situations when used in conjunction with plone.app.theming. 
It does this by letting you define named field sets of MetaData indexed in the Plone catalog in Plones Site Setup.
Data such as publication date, number of comments, author, current state, keywords can all be added to a field set. 
Custom fields can also be created using a TAL expression. The TAL expression can be used to access attributes 
of the content object in order to expose more data about the object. Each field and field set can have custom css classes
associated with them so they can be uniquely styled.

In addition a fieldset can have the following defined:

- view batch size
- portlet batch size
- portlet read more text

You can then use field sets inside plone content as follows:

To customise the listing view of a folder or a collection, pick "Listing View" from the "Display" menu. Your collection
or folder will then have a "Listing Settings" tab. In settings you can pick which field set you'd like to display.
Your content will be displayed as an unordered list (<ul>) of definition terms (<dt>) and definition data (<dd>) for 
each field name and field value. This can be transformed using diazo and css to the style you need.

The ListingView portlet allows you list information about another item. It can work in one of two modes

- absolute: you select a specific collection, folder or content object, 
- or relative: show the contents of the current parent folder or collection (e.g. ".."),
- or relative: it can show information about the current object.(e.g. ".")

Like a collection portlet you can limit the list to just the top options and include read more link. Showing fields
of a specific object, when combined with diazo to customise a content items default view to include additional metadata
of that object in its content view.

Example: Adding publication date news listing
=============================================

Let's say have a design that demands that has a news folder that displays the publication date for each news item.
e.g.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingtop.png

with some extra changes to the batching

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingbottom.png

Most of this can be achieved using diazo and css.

To include publication date with the custom format in the news listing

1. Go to Site Setup > Listing Custom Fields Settings > Add
2. Name it ``Local Publication Date``, enter ``custom-date`` for style class in CSS and enter TAL expression ``object.getObject().modified().strftime("%d/%m/%Y")`` and then Save.
3. Go to Site Setup > Listing View Settings > Add
4. Name it "News with publication", add Location, Title, Description, Local Publication Date fields.
5. Specify a View Batch Size of 10 and a Portlet Batch Size of 5.
6. Go to your news folder and create a collection normally which displays your news sorted by reverse publication date
7. Select Display > Listing View.
8. Click on "Listing Settings", then select "News with publication" and then save.

You will now have a listing that contains all the information you need but doesn't look very nice. It will look
like this

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingraw.png

with html like this

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingtop.png

Next you will need to use diazo rules like the following to turn the bare lising view into the final result

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingtop.png

Example: Adding publication date to a news item
===============================================

Next you'd like to use this same publication date on your news item itself.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/newsitemtop.png

1. Go to Site Setup > Listing View Settings > Add
2. Name it "News Item Info", add just "Local Publication Date" fields.
3. Go to your news folder where all the news items located.
5. Add a "Listing Portlet" portlet to the left side using ``Manage porlets``.
6. Select "news-item" as the portlet header.
7. Select "News Item Info" as the listingview.
7. Left it black for the root path.
8. Opt not to have a border or header, then click save.

Now whenever you view a news item you will get a portlet on the left hand side that contains the following html

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listingportlet.png

Using the diazo mockup and rules.xml to change the final design.

we end up with the desired design.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listinghtml.png

possible future directions
==========================
- make a listingview tile for use in deco or collective.cover. Tile would include querystring to replace collection. If you wanted
 to instead reference a tile elsewhere we might need a referencebrowser widget that lets us pick tiles not just content?
- provide a way to make bulk changes in content from one listingview to another listingview. This would allow a new "template" to be
  created and tested and then switched in production.
- implement safe html filtering
- support customisation of batching settings
- support old style collections
- allow get requests so list can be filtered by custom urls
- support grouping
- support hierarchical listing
- support ajax batching
- support infinite lists (auto load next when scrolled down)
