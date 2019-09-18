
try:
    from plone.app.z3cform.widget import SelectWidget
except ImportError:
    SelectWidget = None

from plone.supermodel import model
from zope.interface import Interface, Attribute
from zope import schema
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter, FactoryAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from collective.listingviews import LVMessageFactory as _
from validation import validate_id, validate_class, validate_tal
try:
    from plone.autoform import directives as form, directives
except ImportError:
    from plone.directives import form
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite


ALL_TYPES = '__alltypes__'


class ICustomFieldDefinition(Interface):
    id = schema.ASCIILine(title=(u"Id"),
                          required=True,
                          description=_(u"It must contains only alphanumeric or underscore, starting with alpha. Will be used as css class"),
                          constraint=validate_id)

    name = schema.ASCIILine(title=_(u"Title"),
                            description=_(u"Name as it will appear in html of view"),
                            required=False)

    tal_statement = schema.ASCIILine(title=_(u"TAL expression"),
                                     required=True,
                                     description=_(u'variables available include "item":catalog brain, "object": context object, "folder": parent of object if object is not a folder. e.g. "python:item.getObject().getBody()"'),
                                     constraint=validate_tal)

    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"),
                                 required=False,
                                 constraint=validate_class,
                                 default=""
                                 )


class IListingDefinition(Interface):
    name = schema.ASCIILine(title=_(u"Title"),
                            required=False,
                            description=_(u"Selectable in Display Menu, Content Listing Tile and Listing View Portlet"))

    id = schema.ASCIILine(title=_(u"Id"),
                          required=True,
                          description=_(
                              u"Unique id and css class"),
                          constraint=validate_id)

    css_class = schema.ASCIILine(title=_(u"CSS classes"),
                                 description=_(u"In addition to id which is used as a class"),
                                 required=False,
                                 constraint=validate_class)

    model.fieldset('sectionA',
                   label=_(u"Section A: Item"),
                   fields=['restricted_to_types', 'item_fields',
                           ]
                   )

    if SelectWidget: form.widget('restricted_to_types', SelectWidget)
    restricted_to_types = schema.List(title=_(u"Enabled on Types"),
                                      description=_(
                                          u"Hide portlet, tile or display menu except for these types"),
                                      required=False,
                                      default=[ALL_TYPES],
                                      value_type=schema.Choice(
                                          vocabulary="collective.listingviews.ContentTypeVocabulary"
                                      ),
                                      )


    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
    if SelectWidget: form.widget('item_fields', SelectWidget)
    item_fields = schema.List(title=_(u"Fields of Item"),
                              description=_(
                                  u"What informaton to display about this folder/collection/item"),
                              required=False,
                              default=[],
                              value_type=schema.Choice(
                                  vocabulary="collective.listingviews.MetadataVocabulary",
                              )
                              )

    model.fieldset('sectionB',
        label=_(u"Section B: Contents"),
        fields=['display_count', 'listing_fields', 'batch_size', 'portlet_more_text'
                ]
        )

    display_count = schema.Bool(title=_(u"Total"),
                                description=_(u"Display a count of the total number of items"),
                                required=False,
                                default=False)

    if SelectWidget: form.widget('listing_fields', SelectWidget)
    listing_fields = schema.List(title=_(u"Fields of Contents"),
                                 description=_(
                                     u"What information to list about the collection/folder contents"),
                                 required=False,
                                 default=[],
                                 value_type=schema.Choice(
                                     vocabulary="collective.listingviews.MetadataVocabulary",
                                 )
                                 )

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size/Limit"),
        description=_(u"description_batch_size",
                      default=u"The amount of items shown in one page. "
                              u"Enter zero if you want to disable view batching."
        ),
        default=10,
        required=True)

    portlet_more_text = schema.ASCIILine(
        title=_(u"Read More Text"),
        description=_(u"If set, limits results and replaces batch with a link"),
        required=False,
    )



#class IListingSettings(Interface):
#    listing_choice = schema.Choice(
#        title=_(u"label_listing_choice", default=u"Listing views"),
#        description=_(u"description_listing_choice",
#            default=u"Select the custom listing views."),
#        vocabulary="collective.listingviews.ListingViewVocabulary",
#        default="view1")


class IListingControlSettings(Interface):
    pass


class IListingControlPanel(Interface):
    views = schema.List(
        title=_(u'Custom listing views'),
        description=(
        u"Create and manage your custom listing views which can be used in collections, folders, portlets and tiles"),
        value_type=schema.Object(IListingDefinition,
                                 title=_(u"Listing View")),
        required=False,
        default=[],
        missing_value=[],
    )


class IListingCustomFieldControlPanel(Interface):
    fields = schema.Tuple(
        title=_(u'Names of custom listing fields'),
        description=_(
        u"Create new fields to insert into your Listing Views based on existing fields of data from your content"),
        value_type=schema.Object(ICustomFieldDefinition,
                                 title=_(u"Custom Field Definition")),
        required=False,
        default=(),
        missing_value=(),
    )


class ListingDefinition(object):
    implements(IListingDefinition)

    def __init__(self, data={}):
        for key,value in data.items():
            setattr(self, key, value)


class ListingDefinitionFactory(FactoryAdapter):
    factory = ListingDefinition


class CustomFieldDefinition(object):
    implements(ICustomFieldDefinition)

    def __init__(self, data={}):
        for key,value in data.items():
            setattr(self, key, value)


class CustomFieldDefinitionFactory(FactoryAdapter):
    factory = CustomFieldDefinition


class IListingAdapter(Interface):
    def retrieve_context_item(self):
        """
        This method retrieves all the item fields
        """

    def retrieve_listing_items(self):
        """
        This method retrieves all the listing fields
        """

    def number_of_items(self):
        """
        Total items of the current list
        """

    def listing_style_class(self):
        """
        Listing view css class
        """

    def listing_view_batch_size(self):
        """
        Batch size
        """

    def set_listing_view(self, view_name):
        """
        Set id of the view to one of the available views stored in the registry.
        """

    def is_container(self):
        """
        Return true if current object is a container, such as folder, or collection
        """

class IListingViewsBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
