from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements
import inspect
from collective.listingviews.browser.views.base import BaseListingInformationRetriever
from collective.listingviews.browser.views.listing_view import ListingView
from collective.listingviews.interfaces import IListingAdapter
from collective.listingviews.utils import getListingNameFromView


class QueryBuilderListingViewAdapter(BaseListingInformationRetriever):
    implements(IListingAdapter)

    def __init__(self, context, querybuilder, request):
        super(QueryBuilderListingViewAdapter,self).__init__(context, request)
        self.results = querybuilder

    @property
    def retrieve_listing_items(self):
        # we were adapted from a QueryBuilder object (which has no interface unfortunatly).
        return self.results



class ContentListingTileView(BrowserView):
    index = ViewPageTemplateFile("contentlisting_tile.pt")

    listing_macros = ListingView.index

    def __init__(self, context, request, name):
        super(ContentListingTileView, self).__init__(context, request)
        self.__adapter_name__ = name

    def render(self):
        return self.index()

    def __call__(self, original_context):
        self.original_context = original_context


        self.listing_view_adapter = QueryBuilderListingViewAdapter(original_context, querybuilder=self.context, request=self.request)
        view_name = getListingNameFromView(self.__adapter_name__)

        self.listing_view_adapter.set_listing_view(view_name)

        return self.render()

    @property
    def macros(self):
        return self.index.macros
