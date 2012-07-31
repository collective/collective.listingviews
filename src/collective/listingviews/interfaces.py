from zope.interface import Interface, Attribute
from zope import schema
from collective.listingviews import LVMessageFactory as _


class IListingViews(Interface):
    """
    marker interface for content types that implement
    the listing views
    """
    pass


class IListingSettings(Interface):
    listing_choice = schema.Choice(
        title=_(u"label_listing_choice", default=u"Listing views"),
        description=_(u"description_listing_choice",
            default=u"Select the custom listing views."),
        vocabulary="collective.listingviews.ListingViewVocabulary",
        default="view1")


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
    def getListingItems(self, listing_fields):
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
