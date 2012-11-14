from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements
from collective.listingviews.interfaces import IListingViews
from collective.listingviews.settings import ListingSettings
#from collective.listingviews.utils import getListingAdapter
from collective.listingviews.adapters import BasicAdapter

class TempSettings(object):
    listing_choice = None



class ListingView(BrowserView):
    """
    
    """
    implements(IListingViews)
    index = ViewPageTemplateFile("templates/layout.pt")

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        view_name = request.getURL().split('/')[-1]
        listing_view_name = view_name.rsplit('.',1)[-1]
        #self.settings = ListingSettings(self.context, interfaces=[self.adapter.schema])
        self.settings = TempSettings()
        self.settings.listing_choice = listing_view_name
        self.adapter = BasicAdapter(self.context, self.request)

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()