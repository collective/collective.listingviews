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

>>> item2_date_pos = browser.contents.find("31/12/2000")
>>> item1_date_pos = browser.contents.find("01/01/2001")

Make sure they are actually present

>>> item1_date_pos == -1
False
>>> item2_date_pos == -1
False

Check that item2's effective date occurs before item1's effective date

>>> (item2_date_pos,item1_date_pos), item2_date_pos < item1_date_pos
((...,...), True)