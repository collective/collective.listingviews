from zope.interface import Interface
from zope import schema
from collective.listingviews import LVMessageFactory as _


class IListingViews(Interface):
    pass


class IListingSettings(Interface):
    listing_choice = schema.Choice(
        title=_(u"label_listing_choice", default=u"Listing views"),
        description=_(u"description_listing_choice",
            default=u"Select the custom listing views."),
        vocabulary="collective.listingviews.ListingViewVocabulary",
        default="view1")
