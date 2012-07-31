import time
import random

from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingAdapter, IListingViews
from collective.listingviews.settings import ListingSettings

from zLOG import LOG, INFO

from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
try:
    from plone.uuid.interfaces import IUUID
except:
    def IUUID(_, _2=None):
        return None


class BaseAdapter(object):

    implements(IListingAdapter)
    adapts(IListingViews, IDefaultBrowserLayer)

    sizes = {}
    settings = None
    schema = None
    name = u"base"
    description = _(u"label_base_gallery_type",
        default=u"base: this isn't actually a gallery type.  "
                u"Think abstract class here...")

    def __init__(self, listing, request):
        self.listing = listing
        self.request = request
        self.settings = ListingSettings(self.listing, interfaces=[self.schema])

    def log_error(self, ex='', inst='', msg=""):
        LOG('collective.plonetruegallery', INFO,
            "%s adapter, gallery is %s\n%s\n%s\n%s" %
            (self.name, str(self.listing), msg, ex, inst))

    def retrieve_items(self):
        raise Exception("Not implemented")

    @property
    def number_of_items(self):
        return 0


class BaseListingInformationRetriever(object):

    def __init__(self, context, listing_adapter):
        self.pm = getToolByName(context, 'portal_membership')
        self.context = context
        self.listing_adapter = listing_adapter
