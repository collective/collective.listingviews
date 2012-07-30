from zope.interface import implements
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import getMultiAdapter
from settings import ListingSettings
from interfaces import IListingSettings
from collective.listingviews.interfaces import IBasicAdapter
from collective.listingviews.interfaces import IListingAdapter, IListingViews
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import string


def getListingAdapter(listing, request):
    return getMultiAdapter((listing, request), IBasicAdapter)


def createSettingsFactory(schema):
    class Settings(ListingSettings):
        implements(schema)

        def __init__(self, context, interfaces=[schema]):
            super(Settings, self).__init__(context, interfaces)

    return Settings

