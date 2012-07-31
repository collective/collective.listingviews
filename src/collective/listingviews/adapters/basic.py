from collective.listingviews.interfaces import IBasicAdapter,\
    IBasicListingSettings, IListingInformationRetriever, IListingAdapter
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import adapts
from base import BaseAdapter, BaseListingInformationRetriever
from collective.listingviews import LVMessageFactory as _
from Products.ATContentTypes.interface import IATTopic
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
        return ['Title', 'Description', 'Path']

    def retrieve_items(self):
        adapter = getMultiAdapter((self.listing, self),
            IListingInformationRetriever)
        return adapter.getListingItems(self.listing_fields)

    @property
    def number_of_items(self):
        return len(self.retrieve_items())


class BasicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

    def getListingItems(self, listing_fields):
        """
        A catalog search should be faster especially when there
        are a large number of images in the gallery. No need
        to wake up all the image objects.
        """
        import pdb; pdb.set_trace()
        items = []
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        brains = self.context.portal_catalog(path={"query" : path, "depth" : 1})
        for brain in brains:
            item = brain.getObject()
            current = []
            for field in listing_fields:
                try:
                    if field.lower() == 'path':
                        attr_value = getattr(item, 'getPhysicalPath', None)
                    else:
                        attr_value = getattr(item, field, None)

                    if not attr_value:
                        continue

                    value = attr_value()
                    if isinstance(value, basestring):
                        value = value.decode("utf-8")
                    elif field.lower() == 'path' or field.lower() == 'getphysicalpath':
                        value = "/".join(value)
                    current.append({'title': field, 'value': value})
                except KeyError:
                    # deal with missing keys
                    pass
            if current:
                items.append(current)
        return items


class BasicTopicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IATTopic, IBasicAdapter)

    def getListingItems(self, listing_fields):
        import pdb; pdb.set_trace()
        return ['one']
