from zope.interface import Interface, Attribute
from zope import schema
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter
from plone.registry.field import PersistentField
from collective.listingviews import LVMessageFactory as _


class IListingViews(Interface):
    """
    marker interface for content types that implement
    the listing views
    """
    pass


class PersistentObject(PersistentField, schema.Object):
    pass


class IListingDefinition(Interface):
    name = schema.ASCIILine(title=_(u"Facet Name"), required=True)
    description = schema.ASCIILine(title=_(u"Description"), required=False)

    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
    metadata_list = schema.List(title=u"Available fields",
                                description=u"Select list fields here",
                                required=True, default=[],
                                value_type=schema.Choice(
                                    vocabulary="collective.listingviews.MetadataVocabulary"),
                                )

    css_class = schema.ASCIILine(title=_(u"Style class in CSS"), required=False)

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"View Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of items shown in one page. "
                    u"Enter zero if you want to disable view batching."
        ),
        default=10,
        required=True)


class ListingDefinition(object):
    implements(IListingDefinition)

registerFactoryAdapter(IListingDefinition, ListingDefinition)


class ICustomFieldDefinition(Interface):
    name = schema.ASCIILine(title=_(u"Field Name"), required=True)
    description = schema.ASCIILine(title=_(u"Description"), required=False)
    css_class = schema.ASCIILine(title=_(u"Style class in CSS"), required=True)
    tal_statement = schema.ASCIILine(title=_(u"TAL statement"), required=True)


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
    views = schema.Tuple(
            title=_(u'Custom listing view'),
            description=(u"Names of custom listing view"),
            value_type=PersistentObject(IListingDefinition,
                title=_(u"Listing Definition")),
            required=False,
            default=(),
            missing_value=(),
    )


class IListingCustomFieldControlPanel(Interface):
    fields = schema.Tuple(
            title=_(u'Manage Custom Listing Fields'),
            description=(u"Names of custom listing fields"),
            value_type=PersistentObject(ICustomFieldDefinition,
                title=_(u"Custom Field Definition")),
            required=False,
            default=(),
            missing_value=(),
    )


class IListingAdapter(Interface):
    sizes = Attribute("size of the fields")
    schema = Attribute("Schema of listing view")
    name = Attribute("Name of the listing view")
    description = Attribute("Description of listing view")

    def log_error(self):
        """
        provides an easy way to log errors in adapters.
        we don't want an adapter to prevent a page from loading...
        """

    def retrieve_items(self):
        """
        This method retrieves all the fields
        """

    def number_of_items(self):
        """"""


class IBasicAdapter(IListingAdapter):
    """
    Use plone to manage listing.
    """
    pass


class IBaseSettings(Interface):
    pass


class IBasicListingSettings(IBaseSettings):
    pass


class IListingInformationRetriever(Interface):
    """
    This interface is interesting for everybody who wants to filter
    the items to be shown in a listing view
    """
    def getListingItems(self):
        """
        Return a list of Information relevant for the view for each
        fields.
        Size should be a hint of the fields size.

        This information returned consists of:
        title
            The view title
        description
            The view description
        """
