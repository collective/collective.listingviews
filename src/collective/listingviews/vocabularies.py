from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from utils import ComplexRecordsProxy
from interfaces import IListingCustomFieldControlPanel, IListingControlPanel
from collective.listingviews import LVMessageFactory as _


class LVVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
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


def ListingViewVocabulary(context):
    terms = []
    reg = queryUtility(IRegistry)
    if reg is not None:
        proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views': 'id'})
        for view in proxy.views:
            terms.append(SimpleVocabulary.createTerm(view.id, view.id, view.name))
    return SimpleVocabulary(terms)


def MetadataVocabulary(context):
    """
    Metadata name is stored in registry. Format for default name is "fieldname:"
    and format for custom name is ":customname"
    """
    terms = []
    portal = getSite()
    metadataDisplay = getToolByName(portal, 'portal_atct').getMetadataDisplay()
    for name, display_name in metadataDisplay.items():
        if name in ['end', 'EffectiveDate', 'start', 'ExpirationDate', 'ModificationDate', 'CreationDate']:
            for format,format_name in [('localshort', 'Date'),('locallong','Date & Time')]:
                terms.append(SimpleVocabulary.createTerm("%s:%s"% (name, format), None,
                                                         "%s (%s)"%(display_name, format_name)))
        else:
            terms.append(SimpleVocabulary.createTerm(name + ":", None, display_name))

    # custom field
    reg = queryUtility(IRegistry)
    if reg is not None:
        proxy = ComplexRecordsProxy(reg, IListingCustomFieldControlPanel,
                                    prefix='collective.listingviews.customfield',
                                   key_names={'fields': 'id'})
        for field in proxy.fields:
            terms.append(SimpleVocabulary.createTerm(':' + field.id, None,
                                                     "%s (Custom)" % field.name))
    return SimpleVocabulary(terms)


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
