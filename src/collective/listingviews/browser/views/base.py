import Missing
from DateTime import DateTime
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingAdapter, \
    IListingInformationRetriever, IListingCustomFieldControlPanel, IListingControlPanel
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
    implements(IListingAdapter, IListingInformationRetriever)

    sizes = {}

    def __init__(self, context, request):
        self.context = context
        self.request = request

        #Tricky part to work out the listing view thats been picked
        if IFacetedLayout is not None and \
            (IFacetedSearchMode.providedBy(self.context) or IFacetedNavigable.providedBy(self.context)):
            # Case: It's being used from facetednavigation
            self.setListingView( getListingNameFromView(IFacetedLayout(self.context).layout) )
        else:
            # Case: It's being used from a normal display menu view
            view_name = request.getURL().split('/')[-1]
            self.setListingView( getListingNameFromView(view_name) )
        # Case: portlet will call setListingView itself


        self.context = context
#        self._field_attribute_name = None
#        self.item_fields = []
        #TODO: this won't work with p.a.collections
        self.metadata_display = dict(getToolByName(context, 'portal_atct').getMetadataDisplay().items())

    def setListingView(self, view_name):
        self.listing_name = view_name
        viewsdata = getRegistryViews()
        for view in viewsdata.views:
            if view.id == self.listing_name:
                self.view_setting = view
                break
        assert self.view_setting is not None



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

    #retriever fields


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
        item = brain
        current = []
        #TODO: this is inefficient to do on every iteration. need to move to setListingView and turn to functions
        for field in self.view_setting.listing_fields:
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
                        plone = getMultiAdapter((self.context, self.request), name="plone")
                        attr_value = plone.toLocalizedTime(attr_value, long_format=1)
                    elif isinstance(attr_value, basestring):
                        attr_value = attr_value.decode("utf-8")

                    css_class = field
                    if field in self.metadata_display:
                        field = self.metadata_display[field]

                    current.append({'title': field, 'css_class': css_class, 'value': attr_value, 'is_custom': False})
                elif not subfield[0]:
                    # custom field name is ":customname"
                    field_name = subfield[1]

                    field = None
                    for field in getRegistryFields().fields:
                        if field.name == field_name:
                            break
                    if field is None:
                        raise Exception("Custom field not recognised '%'"%field_name)


                    # example tal statement
                    # python:'<em>{0}</em>'.format(object.getObject().modified().strftime("%A, %d. %B %Y %I:%M%p"))
                    # python:'{0}'.format(object.getObject().effective().strftime("%d/%m/%Y"))
                    # python:object.getObject().folder_full_view_item()
                    # python:getattr(object.getObject(), 'remote_url', None) and object.getObject().remote_url() for atlink content type
                    try:
                        expression = Expression(field.tal_statement)
                        expression_context = getExprContext(self.context, item)
                        attr_value = expression(expression_context)
                    except ValueError:
                        attr_value = ""

                    current.append({'title': field.name, 'css_class': field.css_class, 'value': attr_value, 'is_custom': True})

                else:
                    print "No valid field"
            except KeyError:
                # deal with missing keys
                pass

        return current
