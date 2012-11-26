from zope.interface import Interface, Attribute
from zope import schema
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter
from collective.listingviews import LVMessageFactory as _
from validation import validate_id, validate_class, validate_tal



class IListingDefinition(Interface):
    id = schema.ASCIILine(title=_(u"Id"),
        required=True,
        description=_(u"Unique id of your listing (will appear as css class). It must contains only alphanumeric or underscore, starting with alpha"),
        constraint=validate_id)

    name = schema.ASCIILine(title=_(u"Title"),
        required=True,
        description=_(u"Name as it will appear in the display menu to editors"))

    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
    item_fields = schema.List(title=_(u"Item Fields"),
        description=_(u"Item fields in the order you want them to appear in your listing"),
        required=True,
        default=[],
        value_type=schema.Choice(
            vocabulary="collective.listingviews.MetadataVocabulary"),
        )

    listing_fields = schema.List(title=_(u"Listing Fields"),
        description=_(u"Listing fields in the order you want them to appear in your listing"),
        required=False,
        default=[],
        value_type=schema.Choice(
            vocabulary="collective.listingviews.MetadataVocabulary"),
        )

    restricted_to_types = schema.List(title=_(u"Restricted To Types"),
        description=_(u"Left it blank if the view is applying all types."),
        required=False,
        default=[],
        value_type=schema.Choice(
            vocabulary="collective.listingviews.ContentTypeVocabulary"),
        )

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"View Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of items shown in one page. "
                    u"Enter zero if you want to disable view batching."
        ),
        default=10,
        required=True)

    portlet_more_text = schema.ASCIILine(title=_(u"Portlet Read More Text"), required=False)

    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"),
        required=False,
        constraint=validate_class)


class ListingDefinition(object):
    implements(IListingDefinition)

registerFactoryAdapter(IListingDefinition, ListingDefinition)


class ICustomFieldDefinition(Interface):
    id = schema.ASCIILine(title=(u"Id"),
        required=True,
        description=_(u"It must contains only alphanumeric or underscore, starting with alpha"),
        constraint=validate_id)

    name = schema.ASCIILine(title=_(u"Title"), required=True)

    tal_statement = schema.ASCIILine(title=_(u"TAL expression"),
                                     required=True,
                                     description=_(u'e.g. "python:item.getObject().getBocy()"'),
                                     constraint=validate_tal)

    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"),
        required=False,
        constraint=validate_class)


class CustomFieldDefinition(object):
    implements(ICustomFieldDefinition)

registerFactoryAdapter(ICustomFieldDefinition, CustomFieldDefinition)


class IListingSettings(Interface):
    listing_choice = schema.Choice(
        title=_(u"label_listing_choice", default=u"Listing views"),
        description=_(u"description_listing_choice",
            default=u"Select the custom listing views."),
        vocabulary="collective.listingviews.ListingViewVocabulary",
        default="view1")


class IListingControlSettings(Interface):
    pass


class IListingControlPanel(Interface):
    views = schema.List(
            title=_(u'Custom listing views'),
            description=(u"Create and manage your custom listing views which can be used in collections, folders, portlets and tiles"),
            value_type=schema.Object(IListingDefinition,
                title=_(u"Listing View")),
            required=False,
            default=[],
            missing_value=[],
    )


class IListingCustomFieldControlPanel(Interface):
    fields = schema.Tuple(
            title=_(u'Names of custom listing fields'),
            description=(u"Create new fields to insert into your Listing Views based on existing fields of data from your content"),
            value_type=schema.Object(ICustomFieldDefinition,
                title=_(u"Custom Field Definition")),
            required=False,
            default=(),
            missing_value=(),
    )


class IBaseSettings(Interface):
    pass


class IBasicListingSettings(IBaseSettings):
    pass


class IListingAdapter(Interface):

    def retrieve_items(self):
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

    def set_listing_view(self, view_name):
        """
        Set id of the view to one of the available views stored in the registry.
        """

    def get_listing_fields(self):
        """
        Return listing fields based on the context type
        """
