from zope.browser.interfaces import IBrowserView
from zope.component import adapts, getMultiAdapter, ComponentLookupError
from zope.interface import implementer
from Products.CMFCore.utils import getToolByName
from .basic import BasicListingInformationRetriever
from collective.listingviews.interfaces import IListingAdapter
from plone.memoize.instance import memoize
from Products.CMFPlone.PloneBatch import Batch
try:
    from plone.app.querystring import queryparser
except ImportError:
    pass

@implementer(IListingAdapter)
class BasicTopicListingInformationRetriever(BasicListingInformationRetriever):

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        return self.context.queryCatalog(REQUEST=self.request,batch=True,b_size=self.listing_view_batch_size)


implementer(IListingAdapter)
class ContentTypesCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """

        # Let's get the browser view for the collection
        # and get its' results
        # works for plone.app.contenttypes.interfaces.ICollection

        view = getMultiAdapter((self.context, self.request), name='listing_view')
        #view = view.__of__(self.context)

        results = view.results()
        return results

@implementer(IListingAdapter)
class AppCollectionListingInformationRetriever(
    BasicTopicListingInformationRetriever):

    @property
    @memoize
    def retrieve_listing_items(self):

        return self.context.queryCatalog(batch=True,b_size=self.listing_view_batch_size)
