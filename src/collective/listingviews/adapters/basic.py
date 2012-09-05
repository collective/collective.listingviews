from collective.listingviews.interfaces import IBasicAdapter,\
    IBasicListingSettings, IListingInformationRetriever,\
    IListingAdapter, IListingDefinition
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import adapts
from base import BaseAdapter, BaseListingInformationRetriever
from collective.listingviews import LVMessageFactory as _
from Products.ATContentTypes.interface import IATTopic
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from plone.memoize.instance import memoize
from Products.CMFPlone.PloneBatch import Batch

try:
    from plone.folder.interfaces import IFolder as IBaseFolder
except ImportError:
    from Products.Archetypes.interfaces import IBaseFolder


class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter, IListingAdapter)

    name = u"basic"
    description = _(u"label_default_listing_view",
        default=u"Use Plone To Manage Listing Views")
    schema = IBasicListingSettings
    view_setting = None

    def __init__(self, listing, request):
        super(BasicAdapter, self).__init__(listing, request)
        registry = queryUtility(IRegistry)
        if registry is not None:
            listing_definition = sorted(registry.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view').items())
            for name, records in listing_definition:
                if name == self.settings.listing_choice:
                    self.view_setting = records
                    break

    @property
    def listing_name(self):
        return self.settings.listing_choice

    @property
    def listing_fields(self):
        fields = []
        if self.view_setting:
            fields = getattr(self.view_setting, 'metadata_list', [])
        if fields is None:
            fields = []
        return fields

    @property
    def listing_style_class(self):
        style_class = ""
        if self.view_setting:
            style_class = getattr(self.view_setting, 'css_class', '')
        if style_class is None:
            style_class = ""
        return style_class

    @property
    def listing_view_batch_size(self):
        batch_size = 0
        if self.view_setting:
            batch_size = getattr(self.view_setting, 'batch_size', 0)
        if batch_size is None:
            batch_size = 0
        return batch_size

    def process_items(self):
        adapter = getMultiAdapter((self.listing, self),
            IListingInformationRetriever)
        return adapter.getListingItems()

    @property
    @memoize
    def retrieve_items(self):
        items = self.process_items()
        if self.listing_view_batch_size:
            items = Batch(items,
                self.listing_view_batch_size,
                int(self.request.get('b_start', 0)),
                orphan=1)
        return items

    @property
    def number_of_items(self):
        return len(self.retrieve_items)


class BasicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

    def getListingItems(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        items = self.context.portal_catalog(path={"query": path, "depth": 1})
        return map(self.assemble_listing_information, items)


class BasicTopicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IATTopic, IBasicAdapter)

    def getListingItems(self):
        query = self.context.buildQuery()
        if query is not None:
            should_limit = self.context.getLimitNumber()
            limit = self.context.getItemCount()
            if not limit:  # also make sure we have more than 0 items
                should_limit = False
            if should_limit:
                query['sort_limit'] = limit
            catalog = getToolByName(self.context, 'portal_catalog')
            items = catalog(query)
            if should_limit:
                items = items[:limit]
            return map(self.assemble_listing_information, items)
        else:
            return []
