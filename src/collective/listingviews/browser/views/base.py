import inspect

import Missing
from DateTime import DateTime
from plone.namedfile.interfaces import IAvailableSizes
from zope.schema.interfaces import IVocabularyFactory
from collective.listingviews import LVMessageFactory as _
try:
    from eea.facetednavigation.layout.interfaces import IFacetedLayout
    from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable, IFacetedSearchMode
except ImportError:
    IFacetedLayout = None
    IFacetedNavigable = None
    IFacetedSearchMode = None
from collective.listingviews.interfaces import IListingAdapter
from collective.listingviews.utils import getListingNameFromView, getRegistryViews, getRegistryFields

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility, queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression, getExprContext
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from plone.memoize.instance import memoize
try:
    from plone.app.contenttypes.behaviors.leadimage import ILeadImage
except ImportError:
    ILeadImage = None


class InvalidListingViewField(Expression):
    pass

def getAdapterName():
    for frame, file, lineno, name, line, _ in inspect.stack():
        # HACK
        if 'zope/interface/adapter.py' in file and name == 'queryMultiAdapter':
            return inspect.getargvalues(frame).locals['name']




class BaseListingInformationRetriever(BrowserView):
    implements(IListingAdapter)

    view_setting = None
    item_field_filters = []
    listing_field_filters = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

        vocab = getUtility(IVocabularyFactory, 'collective.listingviews.MetadataVocabulary')(context)
        self.metadata_display = {item.value: item.title for item in vocab}
        #TODO item.title here is the title for the filter on it. We want the one before the filter was added

        plone_util = getMultiAdapter((self.context, self.request), name="plone")
        self.filters = dict(
            localshort = lambda item, value: plone_util.toLocalizedTime(value, long_format=0),
            locallong = lambda item, value: plone_util.toLocalizedTime(value, long_format=1),
            tolink = lambda item, value: '<a href="%s">%s</a>'%(item.getURL(), value),
        )

        # Image filters. Can take a url and turn it into an image
        def get_tag_for_size(size):
            def get_tag(item, url):
                if not url:
                    return ''
                # HACK: Assume url is item/image_field
                try:
                    url, image_field = url.strip('/').rsplit('/', 1)
                except ValueError:
                    return ''
                if size != 'image':
                    return '<img src="{}/@@images/{}/{}" alt="{}"/>'.format(url, image_field, size, item.Title)
                else:
                    return '<img src="{}/@@images/{}" alt="{}"/>'.format(url, image_field, item.Title)
            return get_tag
        for size in list(queryUtility(IAvailableSizes)().keys())+['image']:
            self.filters['img_{}'.format(size)] = get_tag_for_size(size)

    def set_listing_view(self, view_name):
        self.listing_name = view_name
        viewsdata = getRegistryViews()
        for view in viewsdata.views:
            if view.id == self.listing_name:
                self.view_setting = view
                break

        if self.view_setting is None:
            return

        self.item_field_filters = self.retrieve_fields(self.view_setting.item_fields)
        self.listing_field_filters = self.retrieve_fields(self.view_setting.listing_fields)

    def retrieve_fields(self, fields):
        field_expr = []


        def get_filtered(func, filters):
            def filtered(item):
                res = func(item)
                for filter, filter_func in filters:
                    res['value'] = filter_func(res['item'], res['value'])
                    res['css_class'] += "-%s" % filter
                return res
            return filtered

        for field in fields:
            if ":" not in field:
                raise InvalidListingViewField( "No valid field: %s (No colon)" % field )

            filters = field.split(":")
            field = filters.pop(0)
            if not field:
                value_func = self.custom_field(field_name=filters.pop(0))
            elif field == 'lead_image':
                value_func = self.lead_image_field()
            else:
                value_func = self.metadata_field(field)
            try:
                filters = [(filter,self.filters[filter]) for filter in filters if filter]
            except KeyError:
                raise InvalidListingViewField("Filter not found: %s " % filter)
            field_expr.append(value_func if not filters else get_filtered(value_func, filters))
        return field_expr

    @property
    @memoize
    def retrieve_context_item(self):
        """
        A catalog search means we get a brain so custom expressions work with same
        kind of data
        """
        uid = self.get_UID()
        if not uid:
            return []
        #brain = self.catalog.searchResults({'UID': uid})
        brain = self.context.portal_catalog(UID=uid)
        if brain and len(brain) == 1:
            return self.assemble_listing_information(brain[0], False)
        return []

    def retrieve_listing_items(self):
        return []

    @property
    def number_of_items(self):
        return 0

    @property
    def listing_style_class(self):
        style_class = ""
        if self.view_setting:
            style_class = self.view_setting.css_class if self.view_setting.css_class else ''
            style_class += ' '+self.view_setting.id
        if style_class is None:
            style_class = ""
        return style_class.strip()

    @property
    def listing_view_batch_size(self):
        return 0

    @property
    def is_container(self):
        """
        :return: True if current object is a container, such as folder, or collection
        """
        return False

    @property
    def show_view(self):
        """
        :return: True if the the context is valid for this listing view
        """
        types = self.view_setting.restricted_to_types
        return self.context.getPortalTypeName() in types

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

    def assemble_listing_information(self, brain, is_container):
        """
        brain: object that need to be retrieve
        is_container: if true, this will return listing_field
        """
        item = brain
        #switch between listing_fields or item_fields
        retrieve_fields = self.item_field_filters
        # for container, they will have both item and listing field filters
        if is_container:
            retrieve_fields = self.listing_field_filters

        for func in retrieve_fields:
            yield func(item)

    def metadata_field(self, field_name):

        #filter_func = self.filters.get(filter_name, None)

        # key = "%s:%s" % (field_name, filter_name)
        # if key in self.metadata_display:
        #     field = self.metadata_display[key]
        # else:
        #     raise InvalidListingViewField("Field no longer exists '%s'" % field_name)

        #TODO need better function to make valid css class
        css_class = "field-%s" % (field_name)

        def value(item):
            attr_value = getattr(item, field_name, None)

            if attr_value == None or attr_value == Missing.Value:
                value = None
            elif isinstance(attr_value, basestring):
                value = attr_value.decode("utf-8")
            elif callable(attr_value):
                value = attr_value()
            else:
                value = attr_value
            return {'title': field_name, 'css_class': css_class, 'value': value, 'is_custom': False, 'item':item}

        return value

    def custom_field(self, field_name):
        fields = [f for f in getRegistryFields().fields if f.id == field_name]
        if not fields:
            raise InvalidListingViewField("Custom field not recognised '%s'" % field_name)
        else:
            field = fields[0]
        if field.tal_statement is None:
            raise InvalidListingViewField("Custom field TAL is empty '%s'" % field_name)


        # example tal statement
        # python:'<em>{0}</em>'.format(object.getObject().modified().strftime("%A, %d. %B %Y %I:%M%p"))
        # python:'{0}'.format(object.getObject().effective().strftime("%d/%m/%Y") if getattr(object.getObject(), 'effective', None) else "")
        # python:'{0}'.format(object.getObject().effective().strftime("%d/%m/%Y") if object.getObject().effective().year() >= 1900 else "")
        # python:'{0}'.format(object.getObject().effective().strftime("%d %B %Y"))
        # python:object.getObject().folder_full_view_item()
        # python:getattr(object.getObject(), 'remote_url', None) and object.getObject().remote_url() for atlink content type
        expression = Expression(field.tal_statement)
        if field.css_class:
            css_class = "%s %s" % (field_name, field.css_class)
        else:
            css_class = field_name

        def value(item):
            expression_context = getExprContext(self.context, self.context)
            expression_context.setLocal('item', item)
            try:
                val = expression(expression_context)
            except (AttributeError, IndexError, KeyError, NameError, TypeError, ValueError, ZeroDivisionError):
                portal_membership = getToolByName(self, 'portal_membership')
                if not portal_membership.checkPermission('Manage portal', self.context):
                    return None
                val = 'The custom field expression has an error: %s.' % expression.text
            return {'title': field.name, 'css_class': css_class, 'value': val, 'is_custom': True, 'item':item}
        return value

    def lead_image_field(self):

        def getImageUrl(item):
            # TODO: should be able to do this without waking up the object
            if ILeadImage is not None and ILeadImage.providedBy(item.getObject()):
                url = item.getURL() + "/image"
            elif item.portal_type == 'Image':
                url = item.getURL() + "/image"
            elif item.portal_type == 'News Item':
                url = item.getURL() + "/image"
            else:
                url = ''
            return {'title': 'Lead Image', 'css_class': 'field-lead_image', 'value': url, 'is_custom': False, 'item':item}
        return getImageUrl

# Override context creation
