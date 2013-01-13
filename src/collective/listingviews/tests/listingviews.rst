
>>> from plone.testing.z2 import Browser
>>> from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, setRoles, login
>>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
>>> portal = layer['portal']
>>> browser = Browser(portal)
>>> portalURL = portal.absolute_url()
>>> browser.open(portalURL)

>>> browser.open(portal.absolute_url()+'/@@listingviews_controlpanel')

>>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
>>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
>>> browser.getControl(name='submit').click()

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

>>> browser.open(portal.absolute_url()+'/@@listingviewfields_controlpanel')
>>> browser.getControl('Add').click()


2. Name it ``Local Publication Date``, enter ``custom-date`` for ``Style class in CSS`` and enter
   ``python:object.getObject().effective().strftime("%d/%m/%Y")`` for ``TAL expression`` and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-custom-field.png

>>> browser.getControl('Id').value = "pubdate"
>>> browser.getControl('Title').value = "Local Publication Date"
>>> browser.getControl('TAL expression').value = "python:object.getObject().effective().strftime('%d/%m/%Y')"
>>> browser.getControl('Save').click()


3. Go to ``Site Setup > Listing View > Add``

>>> browser.getLink('Listing View').click()
>>> browser.getControl('Add').click()

4. Name it "News with publication", add Title, Location, Local Publication Date fields.

>>> browser.getControl('Id').value = "pubnews"
>>> browser.getForm(id='crud-add-form').getControl('Title', index=0).value = "News with publication"

# HACK: widget creates control using js so have to fake it
>>> form = browser.getControl('Add').mech_form
>>> form.new_control('text','crud.add.form.widgets.item_fields:list', {'value':'Title:'})

>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'Title:'})
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'location:'})
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':'EffectiveDate:localdate'})
>>> form.new_control('text','crud.add.form.widgets.listing_fields:list', {'value':':pubdate'})
>>> form.fixup()


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

>>> browser.getLink('folder1').click()

7. Select ``Display > 'News with publication'``. This will change the folder view to our new view we created.

>>> browser.getLink('News with publication').click()
>>> browser.contents
'...View changed...'

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-setting.png


You will now have a listing that contains all the information you need but doesn't look very nice. It will look
like this

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-raw.png

with html like this::

>>> print browser.contents
<html>...
    <div class="listingviews">
        <div class=" listing-collection-view">
            <ul class="listing-items-view">
                <li class="listing-item">
                    <dl class="listing-fields">
                        <dt class="listing-field field-Title"> Title</dt>
                        <dd class="listing-field field-Title">Bravery awards for Marysville fire</dd>
                        <dt class="listing-field field-Description"> Description</dt>
                        <dd class="listing-field field-Description">Five SES volunteers from Healesville and Marysville were honoured with bravery awards from the Royal Humane Society of Australasia in Melbourne on Friday, 17 February 2012.</dd>
                        <dt class="listing-field field-location"> Location</dt>
                        <dd class="listing-field field-location">http://127.0.0.1:8080/Plone/media/news/news-items/bravery-awards-for-marysville-fire</dd>
                        <dt class="listing-field custom-date"> Local Publication Date</dt>
                        <dd class="listing-field custom-date">12/09/2012</dd>
                    </dl>
                </li>
                ...
            </ul>
        </div>
    </div>
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


Example: Adding publication date to a news item
===============================================

Next you'd like to use this same publication date on the view of your news item itself.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/news-item-top.png

1. Go to ``Site Setup > Listing View > Add``
2. Name it ``News Item Info``, add just ``Local Publication Date`` fields.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-view.png

3. Go to your news folder where all the news items located and Add a ``Listing Portlet`` portlet to the left side using
  ``Manage porlets``. Alternatively you can go to
  ``Site Setup > Types > News Item > Manage Portlets assigned to this content type``.
4. Enter ``news-item`` as the Portlet header.
5. Select ``News Item Info`` as the ``Listing views``.
6. Leave ``Target`` target blank as you want it to display the publication date of the current item.
7. Click ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-setting.png

Now whenever you view a news item you will get a portlet on the left hand side

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-raw.png

with html like this::

    <dl class="portlet portletListing portlet-listing-news-item">
        <dt class="portletHeader">
            <span class="portletTopLeft"></span>
            <span>
               news-item
            </span>
            <span class="portletTopRight"></span>
        </dt>
        <dd class="portletItem odd">
          <ul class="listing-items-portlet">
            <li class="listing-item">
                <dl class="listing-fields">
                    <dt class="listing-field custom-date"> Local Publication Date</dt>
                    <dd class="listing-field custom-date">12/09/2012</dd>
                </dl>
            </li>
          </ul>
        </dd>
      </dl>

Using the diazo mockup and rules.xml to change the final design we can move the publication date below the title
and remove the portlet completely::

    <drop content-children="//dl[contains(@class, 'portlet-listing-news-item')]" />
    <replace css:content="#parent-fieldname-title" if-content="//dl[contains(@class, 'portlet-listing-news-item')]" >
        <xsl:copy-of select="." />
        <div id="publishedDets" class="publishDate">Published <xsl:value-of select="//dl[contains(@class, 'portlet-listing-news-item')]//dd[contains(@class, 'custom-date')]"/></div>
    </replace>

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
