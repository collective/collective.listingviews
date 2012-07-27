from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements
from collective.listingviews.interfaces import IListingViews
from collective.listingviews.settings import ListingSettings
from collective.listingviews.vocabularies import fields

class ListingView(BrowserView):
    """
    View for file will redirect to download if user can't edit it.
    """
    implements(IListingViews)
    select_listing_view = ViewPageTemplateFile("templates/layout.pt")

    def __call__(self):
        self.settings = ListingSettings(self.context)
        print self.settings
        return self.index()

    
