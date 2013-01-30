
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

First we need to create a custom field using TAL since we want a custom date format rather than Plones default

Go to ``Site Setup > Listing Custom Fields > Add``

>>> browser = layer['manager']
>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing Custom Fields').click()
>>> browser.getControl('Add').click()

The ``Id`` is unique and is also used as a CSS class in the final html

>>> browser.getControl('Id').value = "pubdate"

The ``Title`` is what the editor picks from the ``Display Menu`` or in the ``ListingView Portlet``

>>> browser.getControl('Title').value = "Local Publication Date"

Finally the TAL Expression that is evaluated when showing the field. ``item`` is the catalog brain.
``object`` or ``here`` is the context object.

>>> browser.getControl('TAL expression').value = \
...   "python:item.effective.strftime('%d/%m/%Y') if item.EffectiveDate != 'None' else '' "
>>> browser.getControl('Save').click()


Creating a listing view
-----------------------

Now that we've created our custom field we can add a new Listing View via
``Site Setup > Listing View > Add``

>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

Name it "News with publication".

>>> browser.getControl('Id').value = "pubnews"
>>> browser.getControl('Title', index=0).value = "News with publication"

There are two kinds of information a listing view display. Information about the context object called
``Item Fields`` and information about the contents or matched items called ``Listing Fields``.

These fields come from either standard metadata or the custom fields we add.

>>> print '\n'.join( browser.getControl('Title', index=1).control.displayOptions )
Creation Date (Date)
Creation Date (Date & Time)
Creator
Description
Effective Date (Date)
Effective Date (Date & Time)
End Date (Date)
End Date (Date & Time)
Expiration Date (Date)
Expiration Date (Date & Time)
Short Name
Short Name (Link)
Size
Location
Modification Date (Date)
Modification Date (Date & Time)
State
Start Date (Date)
Start Date (Date & Time)
Tags
Title
Title (Link)
Total number of comments
Item Type
Local Publication Date (Custom)

We want to show the ``Title`` of the context object

>>> layer.setInAndOut(browser, ['Title'], index=1)

and  ``Title``, ``Location``, ``Effective Date`` and ``Local Publication Date`` for each of the content items

>>> layer.setInAndOut(browser, ['Title', 'Title (Link)', 'Effective Date (Date)', 'Local Publication Date (Custom)'], index=3)

By default the view will be enabled for all types. We'll enable it for folders and collections

>>> layer.setInAndOut(browser, ['Folder', 'Collection'])
>>> browser.getControl('Add').click()

We can manage our existing listing views including a link to edit the view we just created.

>>> browser.getLink('pubnews')
<Link text='pubnews' url='http://nohost/plone/listingviews_controlpanel/pubnews'>

Using a listing view on a folder
--------------------------------

We have a folder with some pages in it

>>> browser.getLink('folder1').click()
>>> browser.getLink('item1').click()

Select ``Display > 'News with publication'``. This will change the folder view to our new view we created.

>>> browser.getLink('folder1').click()
>>> browser.getLink('News with publication').click()
>>> browser.contents
'...View changed...'


You will now have a listing that contains all the information you need.
We have a definition for the fields of the folder (the context item)

>>> print browser.contents
<...
      <div class="listing-item-fields">
        <dl class="pubnews-item item-fields">
              <dt class="listing-field field-Title">Title</dt>
              <dd class="listing-field field-Title">folder1</dd>
        </dl>
      </div>
...

There is an unordered list of definition lists for every item contained in the folder.

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

The title of ``item1``

>>> print browser.contents
<...
<dt class="listing-field field-Title">Title</dt>
<dd class="listing-field field-Title">item1</dd>
...

A title made into a link to ``item1``

>>> print browser.contents
<...
<dt class="listing-field field-Title-tolink">Title</dt>
<dd class="listing-field field-Title-tolink"><a href="http://nohost/plone/folder1/item1">item1</a></dd>
...


How the default effective date field looks

>>> print browser.contents
<...
<dt class="listing-field field-EffectiveDate-localshort">Effective Date</dt>
<dd class="listing-field field-EffectiveDate-localshort">..., ...</dd>
...

and finally our custom version of the effective date

>>> print browser.contents
<...
<dt class="listing-field pubdate">Local Publication Date</dt>
<dd class="listing-field pubdate">.../.../...</dd>
...

The styling of this view is very basic. With ``Diazo`` we can turn this into a much nicer looking view by
matching against the CSS class ``pubnews-listing``::

    <replace css:content="ul.pubnews-listing">
        <xsl:for-each select="./li[contains(@class, 'listing-item')]">
            <div class="span8">
                <div class="headline">
                    <xsl:element name="a">
                        <xsl:attribute name="href"><xsl:value-of select="./dl/dd[contains(@class, 'field-location')]"/></xsl:attribute>
                        <xsl:value-of select="./dl/dd[contains(@class, 'field-Title')]"/>
                    </xsl:element>
                </div>
                <div id="publishedDets1" class="publishDate">Published <xsl:value-of select="./dl/dd[contains(@class, 'custom-date')]"/></div>
                <div class="description"><xsl:value-of select="./dl/dd[contains(@class, 'field-Description')]"/></div>
                <div class="newsLink">
                    <xsl:element name="a">
                        <xsl:attribute name="href"><xsl:value-of select="./dl/dd[contains(@class, 'field-location')]"/></xsl:attribute>
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

>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

called ``Publication Info``, .

>>> browser.getControl('Id').value = "pubnewsitem"
>>> browser.getControl('Title', index=0).value = "Publication Info"


add ``Local Publication Date`` to the 'item' fields, rather than the listing fields.

>>> layer.setInAndOut(browser, ['Local Publication Date (Custom)'], index=0)


Finally we only want this to be applied to a Page content type

>>> layer.setInAndOut(browser, ['Page'])
>>> browser.getControl('Add').click()


Go to your  folder where all the pages are located

>>> browser.getLink('Home').click()
>>> browser.getLink('folder1').click()

and Add a ``Listing Portlet`` portlet to the left side using
``Manage porlets``. (Alternatively you can go to
``Site Setup > Types > News Item > Manage Portlets assigned to this content type``).

>>> browser.getLink('Manage portlets').click()
>>> browser.getControl('ListingView Portlet', index=1).click()
>>> layer.getFormFromControl(browser.getControl('ListingView Portlet', index=1)).submit()

Enter ``Publication Info`` as the Portlet header.

>>> browser.getControl('Portlet header').value = 'Publication Info'

Select ``Publication Info`` as the ``Listing views``.

>>> browser.getControl('Publication Info').click()


Leave ``Target`` target blank as you want portlet to show information of the current item. Click ``Save``.

>>> browser.getControl('Save').click()


Now whenever you view a news item you will get a portlet on the left hand side

>>> browser.getLink('folder1').click()

Because we restricted which types the view can be applied to we won't see the portlet on the folder

>>> 'portlet-listing-news-item-info' in browser.contents
False

and not because there is an error

>>> 'There was an error while rendering the portlet' in browser.contents
False


We also aren't able to select that view from the display menu because this is a folder not a Page

>>> browser.getLink('Publication Info')
Traceback (most recent call last):
...
LinkNotFoundError

However on the item we can see a listing portlet

>>> browser.getLink('item1').click()
>>> print browser.contents
<...
    <dl class="portlet portletListing portlet-listing-publication-info">
    ...
    </dl>
...

We can see a portlet with the heading ``Publication Info``

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

Our portlet shows data about the context item (in this case item1)

>>> print browser.contents
<...
  <div class="listing-item-fields-portlet">
      <dl class="pubnewsitem-item item-fields">
                  <dt class="listing-field pubdate">Local Publication Date</dt>
                  <dd class="listing-field pubdate">.../.../...</dd>
            </dl>
  </div>
...

and because item1 has no contents we have an empty list

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

We are also able to select this as a view for the item main content as well

>>> browser.getLink('Publication Info')
<Link text='Publication Info' url='...'>

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
>>> browser.getLink('collection1').click()
>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>

Switch to our publication view

Select ``Display > 'News with publication'``.

>>> browser.getLink('collection1').click()
>>> browser.getLink('News with publication').click()
>>> browser.contents
'...View changed...'

And we'll still see item1

>>> browser.getLink('item1')
<Link text='item1' url='http://nohost/plone/folder1/item1'>

and our custom field

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

We'll create a portlet to give us links

>>> browser.getLink('Manage portlets').click()
>>> browser.getControl('ListingView Portlet', index=1).click()
>>> layer.getFormFromControl(browser.getControl('ListingView Portlet', index=1)).submit()


Give the portlet a header.

>>> browser.getControl('Portlet header').value = 'Collection Portlet'

We have a choice of Listing Views to pick from

>>> browser.getControl('Listing views').displayOptions
['(nothing selected)', 'News with publication', 'Publication Info']

Select ``News with publication`` as the ``Listing views``.

>>> browser.getControl('News with publication').click()

We'll make it display collection1

>>> browser.getControl('Save').mech_form.new_control('text','form.root', {'value':'/folder1/collection1'})
>>> browser.getControl('Save').click()

New when we view home we  see the items inside folder1 based on criteria in collection1

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



