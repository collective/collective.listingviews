from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements
from collective.listingviews.interfaces import IListingViews, IBatchingDisplayType
from collective.listingviews.settings import ListingSettings
from collective.listingviews.adapters import BasicAdapter
from Products.CMFPlone.PloneBatch import Batch
from plone.memoize.view import memoize


class ListingView(BrowserView):
    """
    View for file will redirect to download if user can't edit it.
    """
    implements(IListingViews, IBatchingDisplayType)
    select_listing_view = ViewPageTemplateFile("templates/layout.pt")

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        self.adapter = BasicAdapter(self.context, self.request)
        self.settings = ListingSettings(self.context, interfaces=[self.adapter.schema])

    #def __call__(self):
    #    self.adapter = BasicAdapter(self.context, self.request)
    #    self.settings = ListingSettings(self.context, interfaces=[self.adapter.schema])
    #    return self.index()

    def content(self):
        return self.index()

    def is_batch(self):
        return self.adapter.listing_view_batch_size

    @memoize
    def get_b_start(self):
        return int(self.request.get('b_start', 0))

    b_start = property(get_b_start)

    @property
    @memoize
    def batch(self):
        return Batch(self.adapter.retrieve_items, self.adapter.listing_view_batch_size, int(self.b_start), orphan=1)
