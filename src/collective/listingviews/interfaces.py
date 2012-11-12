from zope.interface import Interface, Attribute
from zope import schema
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter
from collective.listingviews import LVMessageFactory as _


class IListingViews(Interface):
    """
    marker interface for content types that implement
    the listing views
    """
    pass


class IListingDefinition(Interface):
    id = schema.ASCIILine(title=_(_(u"Id")),
                          required=True,
                          description=_(u"Unique id of your listing (will appear as css class)"))
    name = schema.ASCIILine(title=_(u"Title"),
                            required=False,
                            description=_(u"Name as it will appear in the display menu to editors"))

    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
    metadata_list = schema.List(title=_(u"Fields"),
                                description=_(u"Fields in the order you want them to appear in your listing"),
                                required=True,
                                default=[],
                                value_type=schema.Choice(
                                    vocabulary="collective.listingviews.MetadataVocabulary"),
                                )

    behavior_choice = schema.Choice(
        title=_(u"label_behavior_choice", default=u"View Behavior"),
        description=_(u"description_behavior_choice",
            default=u"""
                'Always list' - context of folder, collection or parent.
                'Show single item' - always show the information of the contenxt regardless folder or collection."""),
        vocabulary="collective.listingviews.ViewBehaviorVocabulary",
        default="list")

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"View Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of items shown in one page. "
                    u"Enter zero if you want to disable view batching."
        ),
        default=10,
        required=True)

    portlet_more_text = schema.ASCIILine(title=_(u"Portlet Read More Text"), required=False)
    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"), required=False)


class ListingDefinition(object):
    implements(IListingDefinition)

registerFactoryAdapter(IListingDefinition, ListingDefinition)


class ICustomFieldDefinition(Interface):
    id = schema.ASCIILine(title=_(u"Id"), required=True)
    name = schema.ASCIILine(title=_(u"Title"), required=True)
    tal_statement = schema.ASCIILine(title=_(u"TAL expression"),
                                     required=True,
                                     description=_(u'e.g. "python:item.getObject().getBocy()"'))
    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"), required=False)


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
