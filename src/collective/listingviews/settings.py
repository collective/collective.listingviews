from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from interfaces import IListingSettings
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

ANNOTATION_KEY = 'collective.listingviews'


class AnnotationStorage(object):
    def __init__(self, context):
        self.context = context

        try:
            annotations = IAnnotations(context)
            self._metadata = annotations.get(ANNOTATION_KEY, None)
            if self._metadata is None:
                self._metadata = PersistentDict()
                annotations[ANNOTATION_KEY] = self._metadata
        except TypeError:
            self._metadata = {}

    def put(self, name, value):
        self._metadata[name] = value

    def get(self, name, default=None):
        return self._metadata.get(name, default)


class ListingSettings(object):
    """
    Just uses Annotation storage to save and retrieve the data...
    """
    implements(IListingSettings)

    # these are settings for defaults that are not listed
    # in the interface because I don't want them to show up
    # in the schema
    defaults = {
        'last_cooked_time_in_seconds': 0,
        'cooked_images': []
    }

    def __init__(self, context, interfaces=[IListingSettings]):
        """
        The interfaces argument allows you to customize which
        interface these settings implemenet.
        """
        self.context = context

        self._interfaces = interfaces
        if type(self._interfaces) not in (list, tuple):
            self._interfaces = [self._interfaces]
        self._interfaces = list(self._interfaces)
        if IListingSettings not in self._interfaces:
            self._interfaces.append(IListingSettings)
        if None in self._interfaces:
            self._interfaces.remove(None)

        self.storage = AnnotationStorage(context)
        if not IPloneSiteRoot.providedBy(context):
            site = getToolByName(context, 'portal_url').getPortalObject()
            self.default_settings = ListingSettings(site,
                interfaces=interfaces)
        else:
            self.default_settings = None

    def __setattr__(self, name, value):
        if name in ('context', '_metadata', '_interfaces', 'defaults',
                    'storage', 'default_settings'):
            self.__dict__[name] = value
        else:
            self.storage.put(name, value)

    def __getattr__(self, name):
        """
        since we have multiple settings that are possible to be used
        here, we have to interate over those interfaces to find the
        default values here.
        """
        default = None

        #if name in self.defaults:
        #    default = self.defaults[name]

        #if self.default_settings is None:
        #    for iface in self._interfaces:
        #        if name in iface.names():
        #            default = iface[name].default
        #else:
        #    default = getattr(self.default_settings, name)

        value = self.storage.get(name, default)
        return value
