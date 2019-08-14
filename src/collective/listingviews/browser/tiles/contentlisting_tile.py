from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.component import getMultiAdapter


class ContentListingTileView(BrowserView):
    index = ViewPageTemplateFile("contentlisting_tile.pt")

    def __init__(self, context, request):
        super(ContentListingTileView, self).__init__(context, request)

    def render(self):
        return self.index()

    def __call__(self, original_context):
        self.original_context = original_context
        self.context_adapter =  getMultiAdapter((original_context, self.request), name=u'listing_view_adapter')
        #self.adapter.set_listing_view(self.data.listing_choice)

        return self.render()

    @property
    def macros(self):
        return self.index.macros

    @property
    def retrieve_listing_items(self):
        # we were adapted from a QueryBuilder object (which has no interface unfortunatly).
        return self.context

    @property
    def retrieve_context_item(self):
        return self.context_adapter.retrieve_context_item

    @property
    def listing_style_class(self):
        return "myclass"

    @property
    def css_class(self):
        return "myitem"