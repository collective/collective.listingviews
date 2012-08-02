from zope.interface import implements
from zope.component import getMultiAdapter
from settings import ListingSettings
from collective.listingviews.interfaces import IBasicAdapter


def getListingAdapter(listing, request):
    return getMultiAdapter((listing, request), IBasicAdapter)


def createSettingsFactory(schema):
    class Settings(ListingSettings):
        implements(schema)

        def __init__(self, context, interfaces=[schema]):
            super(Settings, self).__init__(context, interfaces)

    return Settings
