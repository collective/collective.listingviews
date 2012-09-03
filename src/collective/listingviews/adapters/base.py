import Missing
from DateTime import DateTime
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingAdapter, IListingViews
from collective.listingviews.settings import ListingSettings
from zLOG import LOG, INFO
from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from collective.listingviews.interfaces import IListingDefinition, ICustomFieldDefinition
from Products.CMFCore.Expression import Expression, getExprContext
from zope.app.component.hooks import getSite


class BaseAdapter(object):

    implements(IListingAdapter)
    adapts(IListingViews, IDefaultBrowserLayer)

    sizes = {}
    settings = None
    schema = None
    name = u"base"
    description = _(u"label_base_listing_view",
        default=u"Think abstract class here...")

    def __init__(self, listing, request):
        self.listing = listing
        self.request = request
        self.settings = ListingSettings(self.listing, interfaces=[self.schema])

    def log_error(self, ex='', inst='', msg=""):
        LOG('collective.listingviews', INFO,
            "%s adapter, listing view is %s\n%s\n%s\n%s" %
            (self.name, str(self.listing), msg, ex, inst))

    def retrieve_items(self):
        raise Exception("Not implemented")

    @property
    def number_of_items(self):
        return 0


class BaseListingInformationRetriever(object):

    def __init__(self, context, listing_adapter):
        portal = getSite()
        self.pm = getToolByName(context, 'portal_membership')
        self.context = context
        self.listing_adapter = listing_adapter
        self.metadata_list = []
        self.metadata_display = dict(getToolByName(portal, 'portal_atct').getMetadataDisplay().items())
        registry = queryUtility(IRegistry)
        if registry is not None:
            self.metadata_list = sorted(registry.collectionOfInterface(ICustomFieldDefinition,
                            prefix='collective.listingviews.customfield').items())

    def assemble_listing_information(self, brain):
        listing_fields = self.listing_adapter.listing_fields
        item = brain
        current = []
        for field in listing_fields:
            try:
                if field[:2] == 'f_':
                    # default field
                    print "Default field"
                    field = field[2:]
                    #if field.lower() == 'path':
                    #    attr_value = getattr(item, 'getPath', None)()
                    #else:
                    attr_value = getattr(item, field, None)

                    if attr_value == None or attr_value == Missing.Value:
                        continue

                    if isinstance(attr_value, DateTime) or\
                        field == 'end' or\
                        field == 'EffectiveDate' or\
                        field == 'start' or\
                        field == 'ExpirationDate' or\
                        field == 'ModificationDate' or\
                        field == 'CreationDate':
                        plone = getMultiAdapter((self.context, self.listing_adapter.request), name="plone")
                        attr_value = plone.toLocalizedTime(attr_value, long_format=1)
                    elif isinstance(attr_value, basestring):
                        attr_value = attr_value.decode("utf-8")
                    elif field.lower() == 'path' or field.lower() == 'getphysicalpath':
                        attr_value = "/".join(attr_value)

                    if field in self.metadata_display:
                        field = self.metadata_display[field]

                    current.append({'title': field, 'value': attr_value})
                elif field[:2] == 'c_':
                    #custom field
                    print "Custom field"
                    field = field[2:]
                    for metadata, fields in self.metadata_list:
                        if metadata != field:
                            continue

                        name = getattr(fields, 'name', '')
                        css_class = getattr(fields, 'css_class', '')
                        tal_statement = getattr(fields, 'tal_statement', '')

                        try:
                            expression = Expression(tal_statement)
                            expression_context = getExprContext(self.context, item)
                            #import pdb; pdb.set_trace()

                            # Evaluate expression by calling
                            # Expression.__call__(). This
                            # will return whatever value expression evaluation gives
                            value = expression(expression_context)
                        except KeyError:
                            value = '{KeyError}'
                        except AttributeError:
                            value = '{AttributeError}'
                        except NameError:
                            value = '{NameError}'

                        try:
                            if value.strip() == "":
                                # Usually empty expression field means that
                                # expression should be True
                                value = True
                        except AttributeError:
                            value = ""

                        if value:
                                # Expression succeeded
                                pass
                        else:
                                pass

                        break

                    current.append({'title': name, 'css_class': css_class, 'value': value})

                else:
                    print "No valid field"
            except KeyError:
                # deal with missing keys
                pass

        return current
