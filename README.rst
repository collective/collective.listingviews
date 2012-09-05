.. contents::

Introduction
============

ListingViews aims to replace the need to override templates for collections, folders, collection porlets or content
views in many situations when used in conjunction with plone.app.theming. 
It does this by letting you define named field sets of MetaData indexed in the Plone catalog in Plones Site Setup.
Data such as Publication Date, number of comments, Author, Current State, Keywords can all be added to a field set. 
Custom fields can also be created using a TAL Expression. The TAL expression can be used to access attributes 
of the content object in order to expose more data about the object. Each field and field set can have custom css classes
associated with them so they can be uniquely styled.

You can then use field sets inside plone content as follows:

To customise the listing view of a folder or a collection, pick "Listing View" from the "Display" menu. Your collection
or folder will then have a "ListingView Settings" tab. In settings you can pick which field set you'd like to display.
Your content will be displayed as an unordered list (<ul>) of definition terms (<dt>) and definition data (<dd>) for 
each field name and field value. This can be transformed using diazo and css to the style you need.

The ListingView portlet allows you either to 

- select a specific collection, folder or content object, 
- show the contents of the current parent folder or collection, 
- or it can show information about the current object. 

Like a collection portlet you can limit the list to just the top options and include read more link. Showing fields
of a specific object, when combined with diazo to customise a content items default view to include additional metadata
of that object in its content view.

Example: Adding publication date news listing and news items
============================================================

#TODO


possible future directions
==========================
- make a listingview tile for use in deco or collective.cover. Tile would include querystring to replace collection.
- implement safe html filtering
- support customisation of batching settings
- support old style collections
- allow get requests so list can be filtered by custom urls
- support grouping
- support hierachical listing