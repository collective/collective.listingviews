from AccessControl import ClassSecurityInfo, Permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements
from collective.listingviews.utils import getListingNameFromView, AdapterWhoKnowsItsName

try:
    from eea.facetednavigation.layout.interfaces import IFacetedLayout
    from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable, IFacetedSearchMode
except:
    IFacetedLayout = None
    IFacetedNavigable = None
    IFacetedSearchMode = None


class ListingView(AdapterWhoKnowsItsName, BrowserView):
    index = ViewPageTemplateFile("templates/layout.pt")

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.view)

    def render(self):
        return self.index()

    security.declareProtected(Permissions.view, '__call__')
    def __call__(self):
        """ Render the view """

        self.listing_view_adapter = getMultiAdapter((self.context, self.request), name='listing_view_adapter')

        if IFacetedLayout is not None and \
                (IFacetedSearchMode.providedBy(self.context) or IFacetedNavigable.providedBy(self.context)):
            # Case: It's being used from facetednavigation
            self.set_listing_view(getListingNameFromView(IFacetedLayout(self.context).layout))
        else:
            view_name = getListingNameFromView(self.__adapter_name__)
            self.listing_view_adapter.set_listing_view(view_name)

        return self.render()

    @property
    def macros(self):
        return self.index.macros