from DateTime import DateTime
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingAdapter, IListingViews
from collective.listingviews.settings import ListingSettings
from zLOG import LOG, INFO
from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.utils import getToolByName


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

    def assemble_listing_information(self, brain):
        listing_fields = self.listing_adapter.listing_fields
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
                elif isinstance(value, DateTime):
                    plone = getMultiAdapter((self.context, self.listing_adapter.request), name="plone")
                    value = plone.toLocalizedTime(value, long_format=1)
                elif field.lower() == 'path' or field.lower() == 'getphysicalpath':
                    value = "/".join(value)

                current.append({'title': field, 'value': value})
            except KeyError:
                # deal with missing keys
                pass

        return current
