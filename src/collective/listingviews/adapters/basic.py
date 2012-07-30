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

    def retrieve_images(self):
        import pdb; pdb.set_trace()
        adapter = getMultiAdapter((self.listing, self),
            IListingInformationRetriever)
        return adapter.getListingInformation()


class BasicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

    def getListingInformation(self):
        """
        A catalog search should be faster especially when there
        are a large number of images in the gallery. No need
        to wake up all the image objects.
        """
        #import pdb; pdb.set_trace()
        return []


class BasicTopicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingInformationRetriever)
    adapts(IATTopic, IBasicAdapter)

    def getListingInformation(self):
        #import pdb; pdb.set_trace()
        return ['one']
