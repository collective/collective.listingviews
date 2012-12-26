from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from basic import BasicTopicListingInformationRetriever
from collective.listingviews.interfaces import IListingAdapter
from plone.app.querystring import queryparser
from plone.memoize.instance import memoize
from Products.CMFPlone.PloneBatch import Batch


class BasicCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):
    implements(IListingAdapter)

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        limit = self.context.limit
        query = queryparser.parseFormquery(self.context,
            self.context.getRawQuery())
        query['sort_limit'] = limit
        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(query)
        items = items[:limit]

        if self.listing_view_batch_size:
            items = Batch(items,
                self.listing_view_batch_size,
                int(self.request.get('b_start', 0)),
                orphan=1)
        return items
