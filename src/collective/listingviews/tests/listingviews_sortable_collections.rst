Listing Views for collections with sort_on and sort_order preserved
-------------------------------------------------------------------
>>> browser = layer['manager']


Our collection has two documents `item1` and `item2`. The
collection is sorted by effective date and reversed.
We therefore expect `item1` with an effective date of 1/1/2001 to 
be placed after `item2` with an earlier effective date of 12/31/2000

>>> browser.getLink('folder1').click()
>>> print browser.contents
<...collection1...>
>>> browser.getLink('collection1').click()

If sorted as expected the effective date of item1 
will show before the effective date of item2

>>> print browser.contents
<...
                              <dd class="listing-field pubdate">31/12/1969</dd>
...
                              <dd class="listing-field pubdate">31/12/1969</dd>
...
                              <dd class="listing-field pubdate">31/12/2000</dd>
...
                              <dd class="listing-field pubdate">01/01/2001</dd>
...
