from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

class LVVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value
    This prevents any issues if a field
    is removed and the user had it selected.
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


def ContentTypeVocabulary(context):
    """
    Vocabulary for all the content types
    """
    # http://developer.plone.org/content/types.html
    portal = getSite()
    site_properties = getToolByName(portal, "portal_properties").site_properties
    not_searched = site_properties.getProperty('types_not_searched', [])

    portal_types = getToolByName(portal, "portal_types")
    types = portal_types.listContentTypes()

    # Get list of content type ids which are not filtered out
    prepared_types = [t for t in types if t not in not_searched]
    terms = [SimpleVocabulary.createTerm(id, None, portal_types[id].title) for id in prepared_types]
    return SimpleVocabulary(terms)
