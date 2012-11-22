from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from basic import BasicTopicListingInformationRetriever
from collective.listingviews.interfaces import IListingAdapter,IListingInformationRetriever
from plone.app.querystring import queryparser


class BasicCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):
    implements(IListingInformationRetriever, IListingAdapter)

    def getListingFields(self):
        limit = self.context.limit
        query = queryparser.parseFormquery(self.context,
            self.context.getRawQuery())
        query['sort_limit'] = limit
        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(query)
        items = items[:limit]
        self.field_attribute_name = 'listing_fields'
        return items
