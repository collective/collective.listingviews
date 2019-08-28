from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements
import inspect
from collective.listingviews.browser.views.base import BaseListingInformationRetriever, getAdapterName
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

    def __init__(self, context, request):
        self.name = getListingNameFromView(getAdapterName())
        super(ContentListingTileView, self).__init__(context, request)

    def render(self):
        return self.index()

    def __call__(self, original_context):
        self.original_context = original_context
        #self.adapter.set_listing_view(self.data.listing_choice)
        self.listing_view_adapter = QueryBuilderListingViewAdapter(original_context, querybuilder=self.context, request=self.request)
        self.listing_view_adapter.set_listing_view(self.name)

        return self.render()

    @property
    def macros(self):
        return self.index.macros
