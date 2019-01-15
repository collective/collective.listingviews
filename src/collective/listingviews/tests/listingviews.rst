
Creating a custom field
-----------------------

Let's say have a design that demands that has a folder displaying the publication date for each item.

Most of this can be achieved using diazo and css however the publication date isn't in any of Plone's default listing
views.
Previously you would have to dig into Plone's code base, find it's folder template implementation and then
use ``jbot`` or ``ZCML`` template overrides to customise the folder listing template.
Not only will you need to learn about TAL, python, packaging and deployment but the end result will make your site
harder to upgrade. Any future enhancements in Plone's folder template will have to be merged back into your patched
overriden template.

Instead here is how you do it using a ListingView.

First we need to create a custom field using TAL since we want a custom date format rather than Plones default.
A TAL Expression like the following will work.

>>> tal = "python:item.effective.strftime('%d/%m/%Y') if item.EffectiveDate != 'None' else '' "

- Go to ``Site Setup > Listing Custom Fields > Add``
- The ``Id`` is unique and is also used as a CSS class in the final html
- The ``Title`` is what the editor picks from the ``Display Menu`` or in the ``ListingView Portlet``
- Finally the TAL Expression that is evaluated when showing the field. ``item`` is the catalog brain.
  ``object`` or ``here`` is the context object. Below is the TAL we are going to use.

>>> browser = layer['manager']
>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing Custom Fields').click()
>>> browser.getControl('Add').click()
>>> browser.getControl('Id').value = "pubdate"
>>> browser.getControl('Title').value = "Local Publication Date"
>>> browser.getControl('TAL expression').value = tal
>>> browser.getControl('Save').click()


Creating a listing view
-----------------------

Now that we've created our custom field we can add a new Listing View via
``Site Setup > Listing View > Add``.

>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

There are two kinds of information a listing view display. Information about the context object called
``Item Fields`` and information about the contents or matched items called ``Listing Fields``.
These fields come from either standard metadata or the custom fields we add.

>>> 'Description' in browser.getControl('Title', index=1).control.displayOptions
True

>>> plone5 = 'EffectiveDate (Date)' in browser.getControl('Title', index=1).control.displayOptions

#>>> print '\n'.join( sorted(browser.getControl('Title', index=1).control.displayOptions) )
Creation Date (Date & Time)
Creation Date (Date)
Creator
Description
Effective Date (Date & Time)
Effective Date (Date)
End Date (Date & Time)
End Date (Date)
Expiration Date (Date & Time)
Expiration Date (Date)
Short Name
Short Name (Link)
Size
Local Publication Date (Custom)
Location
Modification Date (Date & Time)
Modification Date (Date)
State
Start Date (Date & Time)
Start Date (Date)
Tags
Title
Title (Link)
Total number of comments
Item Type
...

By default the view will be enabled for standard content types. These are

>>> options = browser.getControl('Page').control.displayOptions
>>> options = [o for o in options if 'old-style' not in o]
>>> print '\n'.join( options )
Collection
Comment
Event
File
Folder
Image
Link
News Item
Page

In this case we'll create a view called ``News with publication``.
For the context object we'll show

 - ``Title``

for each of the content items

 - ``Title``
 - ``Title (Link)``
 - ``Effective Date``
 - ``Local Publication Date``

and finally we'll enable the view for all content types

>>> browser.getControl('Id').value = "pubnews"
>>> browser.getControl('Title', index=0).value = "News with publication"
>>> layer.setInAndOut(browser, ['Title'], index=1)
>>> if plone5: layer.setInAndOut(browser, ['Title', 'Title (Link)', 'EffectiveDate (Date)', 'Local Publication Date (Custom)'], index=3)
>>> if not plone5: layer.setInAndOut(browser, ['Title', 'Title (Link)', 'Effective Date (Date)', 'Local Publication Date (Custom)'], index=3)
>>> layer.setInAndOut(browser, browser.getControl('Page').control.displayOptions, index=0 )
>>> browser.getControl('Add').click()

We can manage our existing listing views including a link to edit the view we just created.

>>> browser.getLink('pubnews')
<Link text='pubnews' url='http://nohost/plone/listingviews_controlpanel/pubnews'>

Using a listing view on a folder
--------------------------------

We have a ``folder1`` with some pages in including a Page called ``item1``.
Using the ``Display > News with publication`` menu we will change the folder view to
``News with publication`` view we created.

>>> browser.getLink('folder1').click()
>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>
>>> browser.getLink('folder1').click()
>>> browser.getLink('News with publication').click()


You will now have a listing that contains all the information you need.
We have

- a definition for the fields of the folder (the context item)
- an unordered list of definition lists for every item contained in the folder.

  - the title of ``item1``
  - a title made into a link to ``item1``
  - the ``EffectiveDate`` using Plone's default Date format
  - and finally our custom version of the effective date

Note the html is in exactly the same order as we specifed in our view definition


>>> print browser.contents
<...
      <div class="listing-item-fields">
        <dl class="pubnews-item item-fields">
              <dt class="listing-field field-Title">Title</dt>
              <dd class="listing-field field-Title">folder1</dd>
        </dl>
      </div>
...

>>> print browser.contents
<...
      <ul class="pubnews-listing listing-items-view">
          <li class="listing-item">
              <dl class="listing-fields">
              ...
              </dl>
          </li>
      </ul>
...

>>> print browser.contents
<...
    <dt class="listing-field field-Title">Title</dt>
    <dd class="listing-field field-Title">item1</dd>
...

>>> print browser.contents
<...
    <dt class="listing-field field-Title-tolink">Title (Link)</dt>
    <dd class="listing-field field-Title-tolink"><a href="http://nohost/plone/folder1/item1">item1</a></dd>
...

>>> print browser.contents
<...
    <dt class="listing-field field-EffectiveDate-localshort">Effective Date (Date)</dt>
    <dd class="listing-field field-EffectiveDate-localshort">...</dd>
...

>>> print browser.contents
<...
    <dt class="listing-field pubdate">Local Publication Date</dt>
    <dd class="listing-field pubdate"></dd>
...


The styling of this view is very basic. With ``Diazo`` we can turn this into a much nicer looking view by
matching against the CSS class ``pubnews-listing``::

    <replace css:content="ul.pubnews-listing">
        <xsl:for-each select="./li[contains(@class, 'listing-item')]">
            <div class="span8">
                <div class="headline">
                    <xsl:element name="a">
                        <xsl:attribute name="href"><xsl:value-of select="./dl/dd[contains(@class, 'field-Title')]/a/@href"/></xsl:attribute>
                        <xsl:value-of select="./dl/dd[contains(@class, 'field-Title')]"/>
                    </xsl:element>
                </div>
                <div id="publishedDets1" class="publishDate">Published <xsl:value-of select="./dl/dd[contains(@class, 'custom-date')]"/></div>
                <div class="description"><xsl:value-of select="./dl/dd[contains(@class, 'field-Description')]"/></div>
                <div class="newsLink">
                    <xsl:element name="a">
                        <xsl:attribute name="href"><xsl:value-of select="./dl/dd[contains(@class, 'field-Title')]/a/@href"/></xsl:attribute>
                        <xsl:text>Read Full Article</xsl:text>
                    </xsl:element>
                </div>
            </div>
        </xsl:for-each>
    </replace>


Adding publication date to a Page using a portlet
-------------------------------------------------

We can use the same custom publication date field when viewing Page items.

We'll create a new Listing View
called ``Publication Info``, .
add ``Local Publication Date`` to the 'item' fields, rather than the listing fields.

Finally we only want this to be applied to a Page content type

>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()
>>> browser.getControl('Id').value = "pubnewsitem"
>>> browser.getControl('Title', index=0).value = "Publication Info"
>>> layer.setInAndOut(browser, ['Local Publication Date (Custom)'], index=0)
>>> layer.setInAndOut(browser, ['Page'])
>>> browser.getControl('Add').click()


Go to your  folder where all the pages are located
and

1. Add a ``ListingView Portlet`` portlet to the left side using ``Manage porlets``.
2. Enter ``Publication Info`` as the Portlet header.
3. Select ``Publication Info`` as the ``Listing views``.
4. Leave ``Target`` target blank as you want portlet to show information of the current item. Click ``Save``.

Alternatively you can also add the portlet as a Content Type portlet which also ensures it will only be shown only when
viewing this content type. (e.g. ``Site Setup > Types > News Item > Manage Portlets assigned to this content type``).

>>> browser.getLink('Home').click()
>>> browser.getLink('folder1').click()
>>> browser.getLink('Manage portlets').click()
>>> browser.getControl('ListingView Portlet', index=1).click()
>>> layer.getFormFromControl(browser.getControl('ListingView Portlet', index=1)).submit()
>>> browser.getControl('Portlet header').value = 'Publication Info'
>>> browser.getControl('Publication Info').click()
>>> browser.getControl('Save').click()


Now whenever you view a news item you will get a portlet on the left hand side.
We can see

- a portlet with the heading ``Publication Info``.
- Our portlet shows data about the context item (in this case item1)
- and because item1 has no contents we have an empty list in the listing part of the portlet.

>>> browser.getLink('folder1').click()
>>> browser.getLink('item1').click()
>>> print browser.contents
<...
    <dl class="portlet portletListing portlet-listing-publication-info">
    ...
    </dl>
...
>>> print browser.contents
<...
    <dt class="portletHeader">
        <span class="portletTopLeft"></span>
        <span>
           Publication Info
        </span>
        <span class="portletTopRight"></span>
    </dt>
...
>>> print browser.contents
<...
  <div class="listing-item-fields-portlet">
      <dl class="pubnewsitem-item item-fields">
                  <dt class="listing-field pubdate">Local Publication Date</dt>
                  <dd class="listing-field pubdate">.../.../...</dd>
            </dl>
  </div>
...
>>> print browser.contents
<...
    <ul class="pubnewsitem-listing listing-items-view">
    </ul>
...

Using the diazo mockup and rules.xml to change the final design we can move the publication date below the title
and remove the portlet completely::

    <drop content-children="//dl[contains(@class, 'portlet-listing-news-item')]" />
    <replace css:content="#parent-fieldname-title" if-content="//dl[contains(@class, 'portlet-listing-news-item')]" >
        <xsl:copy-of select="." />
        <div id="publishedDets" class="publishDate">Published <xsl:value-of select="//dl[contains(@class, 'portlet-listing-news-item')]//dd[contains(@class, 'custom-date')]"/></div>
    </replace>


Because we restricted which types the view can be applied to we won't see the portlet on the folder.
We also aren't able to select that view from the display menu because this is a folder not a Page.

>>> browser.getLink('folder1').click()
>>> 'portlet-listing-news-item-info' in browser.contents
False
>>> 'There was an error while rendering the portlet' in browser.contents
False
>>> browser.getLink('Publication Info')
Traceback (most recent call last):
...
LinkNotFoundError


Item View on content
--------------------

We are also able to select our ``Publication Info`` view as a view for the ``item1`` main content as well
via the ``Display > Publication Info`` menu.

>>> browser.getLink('folder1').click()
>>> browser.getLink('item1').click()
>>> browser.getLink('Publication Info')
<Link text='Publication Info' url='.../folder1/item1/selectViewTemplate?templateId=collective.listingviews.pubnewsitem'>


Item View portlet for fixed item
--------------------------------
It's also possible to fix a portlet to show information on particular item instead of the current content context.
Edit the portlet and search for ``item1`` in the ``Target`` Field.

>>> browser.getLink('Manage portlets').click()
>>> browser.getLink('Publication Info').click()
>>> browser.getControl('Save').mech_form.new_control('text','form.root', {'value':'/folder1/item1'})
>>> browser.getControl('Save').click()

#TODO show what happens if we pick an item of invalid type

We will now see the portlet at the folder level

>>> browser.getLink('folder1').click()
>>> print browser.contents
<...
  <div class="listing-item-fields-portlet">
      <dl class="pubnewsitem-item item-fields">
          <dt class="listing-field pubdate">Local Publication Date</dt>
          <dd class="listing-field pubdate">.../.../...</dd>
      </dl>
  </div>
...

Listing Views for collections
-----------------------------

We have create a collection in our folder1 called collection1

>>> browser.getLink('folder1').click()
>>> print browser.contents
<...collection1...>
>>> browser.getLink('collection1').click()
>>> assert "There are currently no items in this folder." not in browser.contents
>>> print browser.contents
<...item1...>
>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>

Switch to our publication view

Select ``Display > 'News with publication'``.

>>> browser.getLink('collection1').click()
>>> browser.getLink('News with publication').click()
>>> browser.contents
'...View changed...'

And we'll still see item1
and our custom field

>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>
>>> print browser.contents
<...
<dt class="listing-field pubdate">Local Publication Date</dt>
<dd class="listing-field pubdate">.../.../...</dd>
...

Collection Portlets
-------------------

We can also create a portlet on the home page listing the contents of this collection

On the home page we have no link to item1

>>> browser.getLink('Home').click()
>>> browser.getLink('item1')
Traceback (most recent call last):
...
LinkNotFoundError

We'll create a portlet to give us links.
Give the portlet a header.
We have a choice of Listing Views to pick from.
Select ``News with publication`` as the ``Listing views``.
We can select a specific collection to display by searching by
name for ``collection1`` in the ``Target`` field.

>>> browser.getLink('Manage portlets').click()
>>> browser.getControl('ListingView Portlet', index=1).click()
>>> layer.getFormFromControl(browser.getControl('ListingView Portlet', index=1)).submit()
>>> browser.getControl('Portlet header').value = 'Collection Portlet'
>>> browser.getControl('Listing views').displayOptions
['(nothing selected)', 'News with publication', 'Publication Info']
>>> browser.getControl('News with publication').click()
>>> browser.getControl('Save').mech_form.new_control('text','form.root', {'value':'/folder1/collection1'})
>>> browser.getControl('Save').click()

New when we view home we  see the items inside ``folder1` based on criteria in ``collection1``, so we'll see
a link to the ``item1``

>>> browser.getLink('Home').click()
>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>


Example: News listing in table view
-----------------------------------

Let's say have a design that demands that has a news folder that displays the publication date for each news item in table form.

We just copy our listing view and give it a new class. Add the following to your diazo rules.xml to turn the plain view into a table::

    <replace css:content="ul.listing-items-view">
        <table>
            <tr>
                <th><xsl:value-of select="./li[contains(@class, 'listing-item')][1]/dl/dt[contains(@class, 'field-Title')]"/></th>
                <th><xsl:value-of select="./li[contains(@class, 'listing-item')][1]/dl/dt[contains(@class, 'custom-date')]"/></th>
                <th><xsl:value-of select="./li[contains(@class, 'listing-item')][1]/dl/dt[contains(@class, 'field-Description')]"/></th>
            </tr>
            <xsl:for-each select="./li[contains(@class, 'listing-item')]">
                <tr>
                    <td>
                        <xsl:element name="a">
                            <xsl:attribute name="href"><xsl:value-of select="./dl/dd[contains(@class, 'field-location')]"/></xsl:attribute>
                            <xsl:value-of select="./dl/dd[contains(@class, 'field-Title')]"/>
                        </xsl:element>
                    </td>
                    <td>
                        <p id="publishedDets1" class="publishDate">Published <xsl:value-of select="./dl/dd[contains(@class, 'custom-date')]"/></p>
                    </td>
                    <td>
                        <p class="description"><xsl:value-of select="./dl/dd[contains(@class, 'field-Description')]"/></p>
                    </td>
                </tr>
            </xsl:for-each>
        </table>
    </replace>



