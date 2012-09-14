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
- portlet batch size (#TODO)
- portlet read more text

You can then use field sets inside plone content as follows:

To customise the listing view of a folder or a collection, pick ``Listing View`` from the ``Display`` menu. Your collection
or folder will then have a ``Listing Settings`` tab. In settings you can pick which field set you'd like to display.
Your content will be displayed as an unordered list (*<ul>*) of definition terms (*<dt>*) and definition data (*<dd>*) for 
each field name and field value. This can be transformed using diazo and css to the style you need.

The ListingView portlet allows you list information about another item. It can work in one of two modes

- absolute: you select a specific collection, folder or content object, 
- or relative: show the contents of the current parent folder or collection (e.g. ".."), (#TODO)
- or relative: it can show information about the current object.(e.g. ".") (#TODO)

Like a collection portlet you can limit the list to just the top options and include read more link. Showing fields
of a specific object, when combined with diazo to customise a content items default view to include additional metadata
of that object in its content view.

Example: Adding publication date news listing
=============================================

Let's say have a design that demands that has a news folder that displays the publication date for each news item.
e.g.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-top.png

with some extra changes to the batching

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-bottom.png

Most of this can be achieved using diazo and css.

To include publication date with the custom format in the news listing

1. Go to ``Site Setup > Listing Custom Fields Settings > Add``
2. Name it ``Local Publication Date``, enter ``custom-date`` for ``Style class in CSS`` and enter ``object.getObject().modified().strftime("%d/%m/%Y")`` for ``TAL expression`` and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-custom-field.png

3. Go to ``Site Setup > Listing View Settings > Add``
4. Name it "News with publication", add Title, Description, Location, Local Publication Date fields.
5. Specify a ``View Batch Size`` of 3 and then ``Save``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-global-setting.png

6. Go to your news folder and create a collection normally which displays your news sorted by reverse publication date
7. Select ``Display > Listing View``.
8. Click on ``Listing Settings``, then select ``News with publication`` and then ``Apply``.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-view-global-setting.png

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

Next you'd like to use this same publication date on your news item itself.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/news-item-top.png

1. Go to ``Site Setup > Listing View Settings > Add``
2. Name it ``News Item Info``, add just ``Local Publication Date`` fields.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-portlet-view.png

3. Go to your news folder where all the news items located.
5. Add a ``Listing Portlet`` portlet to the left side using ``Manage porlets``.
6. Enter ``news-item`` as the Portlet header.
. Select ``News Item Info`` as the ``Listing views``.
7. Left it black for the ``Root path``, then click ``Save``.

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

Using the diazo mockup and rules.xml to change the final design::

    <drop content-children="//dl[contains(@class, 'portlet-listing-news-item')]" />
    <replace css:content="#parent-fieldname-title" if-content="//dl[contains(@class, 'portlet-listing-news-item')]" >
        <xsl:copy-of select="." />
        <div id="publishedDets" class="publishDate">Published <xsl:value-of select="//dl[contains(@class, 'portlet-listing-news-item')]//dd[contains(@class, 'custom-date')]"/></div>
    </replace>

Example: News listing in table view
===============================================

Let's say have a design that demands that has a news folder that displays the publication date for each news item in table form.
e.g.

.. image:: https://github.com/collective/collective.listingviews/raw/master/docs/listing-table-view.png

Using the diazo mockup and rules.xml to change the final design::

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
- implement safe html filtering
- support customisation of batching settings
- support old style collections
- allow get requests so list can be filtered by custom urls
- support grouping
- support hierarchical listing
- support ajax batching
- support infinite lists (auto load next when scrolled down)
