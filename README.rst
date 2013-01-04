.. contents::

Introduction
============

ListingViews allows a site administrator to create new views in Plone Site Setup.
A ListingView definition is an order list of fields which will appear as a repeating list of definition
lists in html with a unique css selector. Editors can pick these view from the ``Display`` menu of any item.
For collections and folders it will give you a batched list. For a content item, it will give you just
information about that item. You can also use the same ListingViews in portlets.
For advanced use you can create custom fields using a TAL expression.

The html of the listings is designed to to be simple and easy to theme using diazo.
ListingViews,when used in conjunction with plone.app.theming, aims to replace many of the usecases which
previously have required overriding ZPT templates, for collections, folders, collection, porlets or content views.


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
2. Name it ``Local Publication Date``, enter ``custom-date`` for ``Style class in CSS`` and enter
   ``python:object.getObject().effictive().strftime("%d/%m/%Y")`` for ``TAL expression`` and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-custom-field.png

3. Go to ``Site Setup > Listing View > Add``
4. Name it "News with publication", add Title, Description, Location, Local Publication Date fields.
5. Specify a ``View Batch Size`` of 3 and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-global-setting.png

6. Go to your news folder and create a collection normally which displays your news sorted by reverse publication date
7. Select ``Display > Listing View``.
8. Click on ``Listing Settings``, then select ``News with publication`` and then ``Apply``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-setting.png

You will now have a listing that contains all the information you need but doesn't look very nice. It will look
like this

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-raw.png

with html like this::

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

