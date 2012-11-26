import Missing
from DateTime import DateTime
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingAdapter, \
    IListingCustomFieldControlPanel, IListingControlPanel
from collective.listingviews.settings import ListingSettings
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable, IFacetedSearchMode

try:
    from eea.facetednavigation.layout.interfaces import IFacetedLayout
except:
    IFacetedLayout = None
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
from Products.Five import BrowserView
from collective.listingviews.browser.views.controlpanel import getRegistryFields, getRegistryViews, getListingNameFromView


class BaseListingInformationRetriever(BrowserView):
    implements(IListingAdapter)

    view_setting = None
    field_filters = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

        #TODO: this won't work with p.a.collections
        self.metadata_display = dict(getToolByName(context, 'portal_atct').getMetadataDisplay().items())

        #Tricky part to work out the listing view thats been picked
        if IFacetedLayout is not None and \
            (IFacetedSearchMode.providedBy(self.context) or IFacetedNavigable.providedBy(self.context)):
            # Case: It's being used from facetednavigation
            self.set_listing_view(getListingNameFromView(IFacetedLayout(self.context).layout))
        else:
            # Case: It's being used from a normal display menu view
            view_name = request.getURL().split('/')[-1]
            self.set_listing_view(getListingNameFromView(view_name))
        # Case: portlet will call setListingView itself

#        self._field_attribute_name = None
#        self.item_fields = []

    def set_listing_view(self, view_name):
        self.listing_name = view_name
        viewsdata = getRegistryViews()
        for view in viewsdata.views:
            if view.id == self.listing_name:
                self.view_setting = view
                break

        if self.view_setting is None:
            return

        self.field_filters = []
        #TODO: this is inefficient to do on every iteration. need to move to setListingView and turn to functions
        for field in self.view_setting.listing_fields:
            if ":" not in field:
                print "No valid field: %s (No colon)" % field
                continue

            subfield = field.split(":")

            if len(subfield) is not 2:
                print "No valid field: %s (Too much colon)" % field
                continue

            if not subfield[1]:
                # default field name in Plone is "defaultname:"
                self.field_filters.append(self.metadata_field(field_name=subfield[0]))
            elif not subfield[0]:
                # custom field name is ":customname"
                self.field_filters.append(self.custom_field(field_name=subfield[1]))
            else:
                print "No valid field"

    def retrieve_context_item(self):
        raise Exception("Not implemented")

    def retrieve_listing_items(self):
        raise Exception("Not implemented")

    @property
    def number_of_items(self):
        return 0

    #retriever fields

    @property
    def field_attribute_name(self):
        return self._field_attribute_name

    @field_attribute_name.setter
    def field_attribute_name(self, value):
        self._field_attribute_name = value

    # BrowserView helper method
    def get_UID(self):
        """ AT and Dexterity compatible way to extract UID from a content item """
        # Make sure we don't get UID from parent folder accidentally
        context = self.context.aq_base
        # Returns UID of the context or None if not available
        # Note that UID is always available for all Dexterity 1.1+
        # content and this only can fail if the content is old not migrated
        #uid = context.UID()
        uuid = IUUID(context, None)
        return uuid

    def get_item_fields(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        uid = self.get_UID()
        if not uid:
            return []
        #brain = self.catalog.searchResults({'UID': uid})
        brain = self.context.portal_catalog(UID=uid)
        self.field_attribute_name = 'item_fields'
        if brain and len(brain) == 1:
            return self.assemble_listing_information(brain[0])
        return []

    def assemble_listing_information(self, brain):
        item = brain
        for func in self.field_filters:
            yield func(item)

    def metadata_field(self, field_name):

        plone = getMultiAdapter((self.context, self.request), name="plone")

        if field_name in self.metadata_display:
            field = self.metadata_display[field_name]
        else:
            raise Exception("Field no longer exists '%s'" % field_name)

        def value(item):
            # metadata does not have location
            if field_name == 'location':
                attr_value = getattr(item, 'getURL', None)
                if attr_value:
                    attr_value = attr_value()
            else:
                attr_value = getattr(item, field_name, None)

            if attr_value == None or attr_value == Missing.Value:
                return None
            elif field_name in ['end', 'EffectiveDate', 'start', 'ExpirationDate', 'ModificationDate', 'CreationDate']:
                return plone.toLocalizedTime(attr_value, long_format=1)
            elif isinstance(attr_value, DateTime):
                return plone.toLocalizedTime(attr_value, long_format=1)
            elif isinstance(attr_value, basestring):
                return attr_value.decode("utf-8")
            else:
                return attr_value

        css_class = field_name

        return lambda item: {'title': field, 'css_class': css_class, 'value': value(item), 'is_custom': False}

    def custom_field(self, field_name):
        field = None
        for field in getRegistryFields().fields:
            if field.name == field_name:
                break
        if field is None:
            raise Exception("Custom field not recognised '%'" % field_name)

        # example tal statement
        # python:'<em>{0}</em>'.format(object.getObject().modified().strftime("%A, %d. %B %Y %I:%M%p"))
        # python:'{0}'.format(object.getObject().effective().strftime("%d/%m/%Y"))
        # python:object.getObject().folder_full_view_item()
        # python:getattr(object.getObject(), 'remote_url', None) and object.getObject().remote_url() for atlink content type
        expression = Expression(field.tal_statement)

        def value(item):
            expression_context = getExprContext(self.context, item)
            val = expression(expression_context)
            return {'title': field.name, 'css_class': field.css_class, 'value': val, 'is_custom': True}
        return value
