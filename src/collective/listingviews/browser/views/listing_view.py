from AccessControl import ClassSecurityInfo, Permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements
from collective.listingviews.browser.views.base import getAdapterName
from collective.listingviews.utils import getListingNameFromView


try:
    from eea.facetednavigation.layout.interfaces import IFacetedLayout
    from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable, IFacetedSearchMode
except:
    IFacetedLayout = None
    IFacetedNavigable = None
    IFacetedSearchMode = None


class ListingView(BrowserView):
    index = ViewPageTemplateFile("templates/layout.pt")

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.view)

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        self.listing_view_adapter = getMultiAdapter((context,request), name='listing_view_adapter')

        if IFacetedLayout is not None and \
            (IFacetedSearchMode.providedBy(self.context) or IFacetedNavigable.providedBy(self.context)):
            # Case: It's being used from facetednavigation
            self.set_listing_view(getListingNameFromView(IFacetedLayout(self.context).layout))
        else:
            view_name = getAdapterName()
            self.listing_view_adapter.set_listing_view(getListingNameFromView(view_name))
            # # Case: It's being used from a normal display menu view
            # view_name = request.getURL().split('/')[-1]
            # self.set_listing_view(getListingNameFromView(view_name))

    def render(self):
        return self.index()

    security.declareProtected(Permissions.view, '__call__')
    def __call__(self):
        """ Render the view """
        return self.render()

    @property
    def macros(self):
        return self.index.macros