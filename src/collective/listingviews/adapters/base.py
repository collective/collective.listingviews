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
from collective.listingviews.interfaces import ICustomFieldDefinition
from Products.CMFCore.Expression import Expression, getExprContext
from zope.app.component.hooks import getSite
from plone.uuid.interfaces import IUUID


class BaseAdapter(object):

    implements(IListingAdapter)
    adapts(IListingViews, IDefaultBrowserLayer)

    sizes = {}
    settings = None
    schema = None
    name = u"base"
    description = _(u"label_base_listing_view",
        default=u"Think abstract class here...")

    def __init__(self, listing, request, portlet_settings=None):
        self.listing = listing
        self.request = request
        if portlet_settings:
            self.settings = portlet_settings
        else:
            self.settings = ListingSettings(self.listing, interfaces=[self.schema])

    def log_error(self, ex='', inst='', msg=""):
        LOG('collective.listingviews', INFO,
            "%s adapter, listing view is %s\n%s\n%s\n%s" %
            (self.name, str(self.listing), msg, ex, inst))

    def retrieve_items(self):
        raise Exception("Not implemented")

    def retrieve_listing_items(self):
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
        self._field_attribute_name = None
        self.item_fields = []
        self.metadata_display = dict(getToolByName(portal, 'portal_atct').getMetadataDisplay().items())
        registry = queryUtility(IRegistry)
        if registry is not None:
            self.item_fields = sorted(registry.collectionOfInterface(ICustomFieldDefinition,
                            prefix='collective.listingviews.customfield.fields').items())

    @property
    def field_attribute_name(self):
        return self._field_attribute_name

    @field_attribute_name.setter
    def field_attribute_name(self, value):
        self._field_attribute_name = value

    # BrowserView helper method
    def getUID(self):
        """ AT and Dexterity compatible way to extract UID from a content item """
        # Make sure we don't get UID from parent folder accidentally
        context = self.context.aq_base
        # Returns UID of the context or None if not available
        # Note that UID is always available for all Dexterity 1.1+
        # content and this only can fail if the content is old not migrated
        #uid = context.UID()
        uuid = IUUID(context, None)
        return uuid

    def getItemFields(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        import pdb; pdb.set_trace()
        uid = self.getUID()
        if not uid:
            return []
        #brain = self.catalog.searchResults({'UID': uid})
        brain = self.context.portal_catalog(UID=uid)
        self.field_attribute_name = 'item_fields'
        if brain and len(brain) == 1:
            return self.assemble_listing_information(brain[0])
        return []

    def assemble_listing_information(self, brain):
        listing_fields = getattr(self.listing_adapter, self._field_attribute_name)
        item = brain
        current = []
        for field in listing_fields:
            try:
                if ":" not in field:
                    print "No valid field: %s (No colon)" % field
                    continue

                subfield = field.split(":")

                if len(subfield) is not 2:
                    print "No valid field: %s (Too much colon)" % field
                    continue

                if not subfield[1]:
                    # default field name in Plone is "defaultname:"
                    field = subfield[0]

                    # metadata does not have location
                    if field == 'location':
                        attr_value = getattr(item, 'getURL', None)
                        if attr_value:
                            attr_value = attr_value()
                    else:
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

                    css_class = field
                    if field in self.metadata_display:
                        field = self.metadata_display[field]

                    current.append({'title': field, 'css_class': css_class, 'value': attr_value, 'is_custom': False})
                elif not subfield[0]:
                    # custom field name is ":customname"
                    field = subfield[1]

                    if not self.item_fields:
                        continue

                    for metadata, fields in self.item_fields:
                        if metadata != field:
                            continue

                        name = getattr(fields, 'name', '')
                        css_class = getattr(fields, 'css_class', '')
                        tal_statement = getattr(fields, 'tal_statement', '')

                        # example tal statement
                        # python:'<em>{0}</em>'.format(object.getObject().modified().strftime("%A, %d. %B %Y %I:%M%p"))
                        # python:'{0}'.format(object.getObject().modified().strftime("%d/%m/%Y"))
                        # python:object.getObject().folder_full_view_item()
                        expression = Expression(tal_statement)
                        expression_context = getExprContext(self.context, item)
                        attr_value = expression(expression_context)
                        break

                    current.append({'title': name, 'css_class': css_class, 'value': attr_value, 'is_custom': True})

                else:
                    print "No valid field"
            except KeyError:
                # deal with missing keys
                pass

        return current
