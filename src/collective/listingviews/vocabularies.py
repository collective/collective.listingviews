from zope.schema.vocabulary import SimpleVocabulary
from collective.listingviews.interfaces import IListingDefinition
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite


class LVVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
    This prevents any issues if a gallery or display
    type is removed and the user had it selected.
    """

    def __init__(self, terms, *interfaces, **config):
        try:
            super(LVVocabulary, self).__init__(terms, *interfaces)
        except:
            import pdb
            pdb.set_trace()
            raise
        if 'default' in config:
            self.default = config['default']
        else:
            self.default = None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)

#Temp object
list_views = [{'name':'view1', 'description':'listing view1'},
    {'name':'view2', 'description':'listing view2'},
    {'name':'view3', 'description':'listing view3'},
    {'name':'view4', 'description':'listing view4'},
    {'name':'view5', 'description':'listing view5'},
    {'name':'view6', 'description':'listing view6'},
    {'name':'view7', 'description':'listing view7'},
    {'name':'view8', 'description':'listing view8'}]
GLOBAL_FIELDS = {
    'view0': ['Title'],
    'view1': ['Title', 'Description', 'Path', 'modified'],
    'view2': ['Title', 'Description'],
    'view3': ['Title', 'Path'],
    'view4': ['Title', 'modified'],
    'view5': ['Title', 'Path', 'modified'],
    'view6': ['Title', 'Description', 'modified'],
    'view7': ['Title', 'Description', 'Path'],
    'view8': ['Path']
    }


def ListingViewVocabulary(context):
    terms = []
    #for t in list_views:
    #    terms.append(SimpleTerm(t['name'], t['name'], t['description']))

    #return LVVocabulary(terms,
    #            default=IListingSettings['listing_choice'].default)
    registry = queryUtility(IRegistry)
    if registry is not None:
        facets = sorted(registry.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view').items())
        for view, fields in facets:
            name = getattr(fields, 'name', '')
            terms.append(SimpleVocabulary.createTerm(view, view, name))
    return SimpleVocabulary(terms)


def MetadataVocabulary(context):
    terms = []
    portal = getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    # should use schema or indexes
    for name in catalog.schema():
        terms.append(SimpleVocabulary.createTerm(name, name, name))
    return SimpleVocabulary(terms)
