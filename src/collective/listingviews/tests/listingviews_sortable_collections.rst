Listing Views for collections with sort_on and sort_order preserved
-------------------------------------------------------------------
>>> browser = layer['manager']


- Create a custom publication field

>>> tal = "python:item.effective.strftime('%d/%m/%Y') if item.effective else '' "

- Go to ``Site Setup > Listing Custom Fields > Add``
- The ``Id`` is unique and is also used as a CSS class in the final html
- The ``Title`` is what the editor picks from the ``Display Menu`` or in the ``ListingView Portlet``
- Finally the TAL Expression that is evaluated when showing the field. ``item`` is the catalog brain.
  ``object`` or ``here`` is the context object. Below is the TAL we are going to use.

>>> browser = layer['manager']
>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing Custom Fields').click()
>>> print browser.contents
<...Add...

>>> browser.getControl('Add').click()
>>> browser.getControl('Id', index=0).value = "pubdate"
>>> browser.getControl('Title').value = "Local Publication Date"
>>> browser.getControl('TAL expression').value = tal
>>> browser.getControl('Save').click()
>>> print browser.contents
<...
Changes saved.
...

- Create the listing views for collection

>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Listing View').click()
>>> browser.getControl('Id').value = "pubnews"
>>> browser.getControl('Title', index=0).value = "News with publication"
>>> layer.setInAndOut(browser, ['Title'], index=1)
>>> layer.setInAndOut(browser, ['Title', 'Title (Link)', 'Effective Date (Date)', 'Local Publication Date (Custom)'], index=3)
>>> layer.setInAndOut(browser, ['Page','Folder', 'Collection'], index=0 )
>>> browser.getControl('Add').click()

Our collection has two documents `item1` and `item2`. The
collection is sorted by effective date and reversed.
We therefore expect `item1` with an effective date of 1/1/2001 to 
be placed after `item2` with an earlier effective date of 12/31/2000

>>> browser.getLink('folder1').click()
>>> print browser.contents
<...collection1...>

Using the ``Display > News with publication`` menu we will change the folder view to
``News with publication`` view we created.

>>> browser.getLink('collection1').click()
>>> browser.getLink('News with publication').click()

If sorted as expected the effective date of item1 
will show before the effective date of item2

>>> print browser.contents
<...
...
                              <dd class="listing-field pubdate">31/12/1969</dd>
...
                              <dd class="listing-field pubdate">31/12/1969</dd>
...
                              <dd class="listing-field pubdate">31/12/2000</dd>
...
                              <dd class="listing-field pubdate">01/01/2001</dd>
...
