from zope.component import adapts
from Products.CMFCore.utils import getToolByName
from collective.listingviews.adapters.basic import\
    BasicTopicListingInformationRetriever
from Products.ATContentTypes.interface.image import IImageContent
from plone.app.collection.interfaces import ICollection
from collective.listingviews.interfaces import IBasicAdapter
from plone.app.querystring import queryparser


class BasicCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):
    adapts(ICollection, IBasicAdapter)

    def getListingInformation(self):
        #import pdb; pdb.set_trace()
        return ['one', 'Two']
