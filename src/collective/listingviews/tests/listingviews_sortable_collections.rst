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
>>> browser.contents
<...
<li class="listing-item">
  <dl class="listing-fields">
    <dt class="listing-field field-Title">Title</dt>
    <dd class="listing-field field-Title">item2</dd> 
    <dt class="listing-field field-Title-tolink">Title</dt>
    <dd class="listing-field field-Title-tolink"><a href="http://nohost/plone/folder1/item2">item1</a></dd>
    <dt class="listing-field field-EffectiveDate-localshort">Effective Date</dt>
    <dd class="listing-field field-EffectiveDate-localshort">Dec 31, 2000</dd>
    <dt class="listing-field pubdate">Local Publication Date</dt>
    <dd class="listing-field pubdate">31/12/2000</dd>
  </dl>
</li>
<li class="listing-item">
  <dl class="listing-fields">
    <dt class="listing-field field-Title">Title</dt>
    <dd class="listing-field field-Title">item1</dd> 
    <dt class="listing-field field-Title-tolink">Title</dt>
    <dd class="listing-field field-Title-tolink"><a href="http://nohost/plone/folder1/item1">item1</a></dd>
    <dt class="listing-field field-EffectiveDate-localshort">Effective Date</dt>
    <dd class="listing-field field-EffectiveDate-localshort">Jan 01, 2001</dd>
    <dt class="listing-field pubdate">Local Publication Date</dt>
...