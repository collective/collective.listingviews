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

    # Contains lists of values from Choice list using special "get_field_list" vocabulary
    # We also give a plone.form.directives hint to render this as
    # multiple checbox choices
    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
    metadata_list = schema.List(title=u"Available headers and animations",
                               description=u"Headers and animations uploaded here",
                               required=False, default=[],
                               value_type=schema.Choice(vocabulary="collective.listingviews.MetadataVocabulary"),
                               )


class ListingDefinition(object):
    implements(IListingDefinition)

registerFactoryAdapter(IListingDefinition, ListingDefinition)


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
            value_type=PersistentObject(IListingDefinition, title=_(u"Listing Definition")),
            required=False,
            default=(),
            missing_value=(),
    )


class IListingAdapter(Interface):
    sizes = Attribute("image size mappings for the gallery type")
    schema = Attribute("Schema of gallery specific")
    name = Attribute("Name of the gallery")
    description = Attribute("Description of gallery type")

    def log_error(self):
        """
        provides an easy way to log errors in gallery adapters.
        we don't want an adapter to prevent a page from loading...
        Who knows what kind of odd behavior some adapters may run into
        when working with picasa or flickr apis...
        """

    def retrieve_items(self):
        """
        This method retrieves all the images to be cooked
        """

    def number_of_items(self):
        """"""


class IBasicAdapter(IListingAdapter):
    """
    Use plone to manage images for the gallery.
    """
    pass


class IBaseSettings(Interface):
    pass


class IBasicListingSettings(IBaseSettings):
    pass


class IListingInformationRetriever(Interface):
    """
    This interface is interesting for everybody who wants to filter
    the items to be shown in a gallery view
    """
    def getListingItems(self):
        """
        Return a list of Information relevant for gallery display for each
        image.
        Size should be a hint of the image size to use, in string format.
        The standard implementations support the following sizes, which
        map to the given size of the archetypes Image size:

            small -> mini
            medium -> preview
            large -> large

        This information returned consists of:
        image_url
            The URL to the image itself
        thumb_url
            The URL to a thumbnail version of the image
        link
            The Link to which an image must point to
        title
            The image title
        description
            The image description
        """
