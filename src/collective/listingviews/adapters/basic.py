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

try:
    from plone.folder.interfaces import IFolder as IBaseFolder
except ImportError:
    from Products.Archetypes.interfaces import IBaseFolder


class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter, IListingAdapter)

    name = u"basic"
    description = _(u"label_default_gallery_type",
        default=u"Use Plone To Manage Images")
    schema = IBasicListingSettings

    @property
    def listing_name(self):
        return self.settings.listing_choice

    @property
    def listing_fields(self):
        fields = []
        registry = queryUtility(IRegistry)
        if registry is not None:
            facets = sorted(registry.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view').items())
            for name, records in facets:
                if name == self.settings.listing_choice:
                    fields = getattr(records, 'metadata_list', [])
                    break
        return fields

    def retrieve_items(self):
        adapter = getMultiAdapter((self.listing, self),
            IListingInformationRetriever)
        return adapter.getListingItems()

    @property
    def number_of_items(self):
        return len(self.retrieve_items())


class BasicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

    def getListingItems(self):
        """
        A catalog search should be faster especially when there
        are a large number of images in the gallery. No need
        to wake up all the image objects.
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
