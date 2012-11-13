from zope.component import adapts
from Products.CMFCore.utils import getToolByName
from collective.listingviews.adapters.basic import\
    BasicTopicListingInformationRetriever
from plone.app.collection.interfaces import ICollection
from collective.listingviews.interfaces import IBasicAdapter
from plone.app.querystring import queryparser


class BasicCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):
    adapts(ICollection, IBasicAdapter)

    def getListingFields(self):
        limit = self.context.limit
        query = queryparser.parseFormquery(self.context,
            self.context.getRawQuery())
        query['sort_limit'] = limit
        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(query)
        items = items[:limit]
        self.field_attribute_name = 'listing_fields'
        return map(self.assemble_listing_information, items)
