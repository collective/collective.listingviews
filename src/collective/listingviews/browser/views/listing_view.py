from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements
from collective.listingviews.interfaces import IListingViews

#Temp object
list_views = ['view1', 'view2']
fields = [{'view1': ['title']}, {'view2': ['title', 'description']}]


class ListingView(BrowserView):
    """
    View for file will redirect to download if user can't edit it.
    """
    implements(IListingViews)
    select_listing_view = ViewPageTemplateFile("templates/layout.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

