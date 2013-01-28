
>>> browser = layer['manager']

Example: Adding publication date news listing
=============================================

Let's say have a design that demands that has a news folder that displays the publication date for each news item.


e.g.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-top.png

with some extra changes to the batching

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-bottom.png

Most of this can be achieved using diazo and css however the publication date isn't in any of Plone's default listing
views.
Previously you would have to dig into Plone's code base, find it's folder template implementation and then
use ``jbot`` or ``ZCML`` template overrides to customise the folder listing template.
Not only will you need to learn about TAL, python, packaging and deployment but the end result will make your site
harder to upgrade. Any future enhancements in Plone's folder template will have to be merged back into your patched
overriden template.

Instead here is how you do it using a ListingView.

To include publication date with the custom format in the news listing

1. Go to ``Site Setup > Listing Custom Fields > Add``

>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing Custom Fields').click()
>>> browser.getControl('Add').click()


2. Name it ``Local Publication Date``, enter ``custom-date`` for ``Style class in CSS`` and enter
   a ``TAL expression`` and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-custom-field.png

>>> browser.getControl('Id').value = "pubdate"
>>> browser.getControl('Title').value = "Local Publication Date"
>>> browser.getControl('TAL expression').value = \
...   "python:item.effective.strftime('%d/%m/%Y') if item.EffectiveDate != 'None' else '' "
>>> browser.getControl('Save').click()


3. Go to ``Site Setup > Listing View > Add``

>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

4. Name it "News with publication".

>>> browser.getControl('Id').value = "pubnews"
>>> browser.getForm(id='crud-add-form').getControl('Title', index=0).value = "News with publication"

Can can get the view to list information about the context item and also each item in it contains.
We'll show the ``Title`` of the item

# HACK: widget creates control using js so have to fake it
>>> form = browser.getControl('Add').mech_form
>>> form.new_control('text','crud.add.form.widgets.item_fields:list', {'value':'Title:'})

and  ``Title``, ``Location``, ``Effective Date`` and ``Local Publication Date`` for each of the content items

>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'Title:'}, index=1)
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'Title:tolink'}, index=2)
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'EffectiveDate:localshort'}, index=3)
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':':pubdate'}, index=4)
>>> #form.fixup()

By default the view will be enabled for all types. We'll enable it for folders.

>>> form.new_control('text','crud.add.form.widgets.restricted_to_types:list', {'value':'Folder'}, index=1)


5. Specify a ``View Batch Size`` of 3 and then ``Add``.

>>> browser.getControl('View Batch Size').value = '3'
>>> browser.getControl('Add').click()

We should have a crud form with a link to edit the listing view we just added
>>> browser.getLink('pubnews')
<Link text='pubnews' url='http://nohost/plone/listingviews_controlpanel/pubnews'>

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-global-setting.png

6. Go to your news folder and create a collection normally which displays your news sorted by reverse publication date

>>> browser.getLink('Home').click()
>>> browser.getLink('Folder').click()
>>> browser.getControl('Title').value = 'folder1'
>>> browser.getControl('Save').click()

Add an item
>>> browser.getLink('Page').click()
>>> browser.getControl('Title').value = 'item1'
>>> browser.getControl('Save').click()
>>> browser.getLink('Publish').click()

7. Select ``Display > 'News with publication'``. This will change the folder view to our new view we created.

>>> browser.getLink('folder1').click()
>>> browser.getLink('News with publication').click()
>>> browser.contents
'...View changed...'

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-setting.png


You will now have a listing that contains all the information you need but doesn't look very nice. It will look
like this

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-raw.png


We have a definition for the fields of the folder

>>> print browser.contents
<...
              <div class="listing-item-fields">
                <dl class="-item item-fields">
                      <dt class="listing-field field-Title">Title</dt>
                      <dd class="listing-field field-Title">folder1</dd>
                </dl>
              </div>
...

There is an unordered list of definition lists for every item contained in the folder.
>>> print browser.contents
<...
              <ul class="-listing listing-items-view">
                  <li class="listing-item">
                      <dl class="listing-fields">
                      ...
                      </dl>
                  </li>
              </ul>
...

The title of item1

>>> print browser.contents
<...
<dt class="listing-field field-Title">Title</dt>
<dd class="listing-field field-Title">item1</dd>
...

A title made into a link to item1

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

Next you will need to use diazo rules like the following to turn the bare lising view into the final result::

    <replace css:content="ul.listing-items-view">
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

If you want to change the batching as well, there is an example::

    <replace css:content="div.listingBar">
        <xsl:for-each css:select="div.listingBar span">
            <xsl:choose>
                <xsl:when test="./@class='previous'">
                    <xsl:element name="span">
                        <xsl:attribute name="class"><xsl:value-of select="./@class"/> prev-news-link</xsl:attribute>
                        <xsl:element name="a">
                            <xsl:attribute name="href"><xsl:value-of select="./a/@href"/></xsl:attribute>
                            &lt;&lt; Prev News
                        </xsl:element>
                    </xsl:element>
                </xsl:when>
                <xsl:when test="./@class='next'">
                    <xsl:element name="span">
                        <xsl:attribute name="class"><xsl:value-of select="./@class"/> more-news-link</xsl:attribute>
                        <xsl:element name="a">
                            <xsl:attribute name="href"><xsl:value-of select="./a/@href"/></xsl:attribute>
                            More News &gt;&gt;
                        </xsl:element>
                    </xsl:element>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </replace>


Example: Adding publication date to a Page only via a Portlet
=============================================================

Next you'd like to use this same publication date on the view of your news item itself.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/news-item-top.png

1. Go to ``Site Setup > Listing View > Add``
>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

2. Name it ``News Item Info``, add just ``Local Publication Date`` fields.

>>> browser.getControl('Id').value = "pubnewsitem"
>>> browser.getForm(id='crud-add-form').getControl('Title', index=0).value = "News Item Info"

# HACK: widget creates control using js so have to fake it
>>> form = browser.getControl('Add').mech_form
>>> form.new_control('text','crud.add.form.widgets.item_fields:list', {'value':':pubdate'}, index=4)


Finally we only want this to be applied to a Page content type

#>>> browser.getControl('Restricted To Types').getControl('Page').click()
>>> form.new_control('text','crud.add.form.widgets.restricted_to_types:list', {'value':'Document'}, index=1)

>>> browser.getControl('Add').click()


.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-view.png

3. Go to your news folder where all the news items located and Add a ``Listing Portlet`` portlet to the left side using
  ``Manage porlets``. Alternatively you can go to
  ``Site Setup > Types > News Item > Manage Portlets assigned to this content type``.

>>> browser.getLink('Home').click()
>>> browser.getLink('folder1').click()
>>> browser.getLink('Manage portlets').click()
>>> browser.getControl('Listing Portlet', index=1).click()
>>> layer.getFormFromControl(browser.getControl('Listing Portlet', index=1)).submit()


4. Enter ``News Item Info`` as the Portlet header.

>>> browser.getControl('Portlet header').value = 'News Item Info'

5. Select ``News Item Info`` as the ``Listing views``.

>>> browser.getControl('News Item Info').click()


6. Leave ``Target`` target blank as you want portlet to show information of the current item.
7. Click ``Save``.

>>> browser.getControl('Save').click()


.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-setting.png

Now whenever you view a news item you will get a portlet on the left hand side

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-raw.png

>>> browser.getLink('folder1').click()

Because we restricted which types the view can be applied to we won't see the portlet on the folder
>>> 'portlet-listing-news-item-info' in browser.contents
False

and not because there is an error

>>> 'There was an error while rendering the portlet' in browser.contents
False


We also aren't able to select that view from the display menu because this is a folder not a Page

>>> browser.getLink('News Item Info')
Traceback (most recent call last):
...
LinkNotFoundError

However on the item we can see a listing portlet

>>> browser.getLink('item1').click()
>>> print browser.contents
<...
    <dl class="portlet portletListing portlet-listing-news-item-info">
    ...
    </dl>
...

We can see a portlet with the heading ``News Item Info``

>>> print browser.contents
<...
        <dt class="portletHeader">
            <span class="portletTopLeft"></span>
            <span>
               News Item Info
            </span>
            <span class="portletTopRight"></span>
        </dt>
...

Our portlet shows data about the context item (in this case item1)

>>> print browser.contents
<...
  <div class="listing-item-fields-portlet">
      <dl class="-item item-fields">
                  <dt class="listing-field pubdate">Local Publication Date</dt>
                  <dd class="listing-field pubdate">.../.../...</dd>
            </dl>
  </div>
...

and because item1 has no contents we have an empty list

>>> print browser.contents
<...
    <ul class="-listing listing-items-view">
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

>>> browser.getLink('News Item Info')
<Link text='News Item Info' url='...'>

It's also possible to fix a portlet to show information on particular item instead of the current content context.
Edit the portlet and search for ``item1`` in the ``Target`` Field.

>>> browser.getLink('Manage portlets').click()
>>> browser.getLink('News Item Info').click()
>>> #browser.getControl('Target').value = 'folder1/item1'
>>> form = browser.getControl('Save').mech_form #HACK
>>> form.new_control('text','form.root', {'value':'/folder1/item1'})
>>> browser.getControl('Save').click()

#TODO show what happens if we pick an item of invalid type

We will now see the portlet at the folder level
>>> browser.getLink('folder1').click()

>>> print browser.contents
<...
  <div class="listing-item-fields-portlet">
      <dl class="-item item-fields">
          <dt class="listing-field pubdate">Local Publication Date</dt>
          <dd class="listing-field pubdate">.../.../...</dd>
      </dl>
  </div>
...


Example: News listing in table view
===================================

Let's say have a design that demands that has a news folder that displays the publication date for each news item in table form.
e.g.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-table-view.png

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



#>>> layer.errorlog()


