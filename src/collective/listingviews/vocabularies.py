from zope.schema.vocabulary import SimpleVocabulary
from collective.listingviews.interfaces import IListingDefinition, ICustomFieldDefinition
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from utils import ComplexRecordsProxy
from interfaces import IListingCustomFieldControlPanel, IListingControlPanel


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
                                key_names={'views':'id'})
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
        terms.append(SimpleVocabulary.createTerm(name + ":", None, display_name))

    # custom field
    reg = queryUtility(IRegistry)
    if reg is not None:
        proxy = ComplexRecordsProxy(reg, IListingCustomFieldControlPanel,
                                    prefix='collective.listingviews.customfield',
                                   key_names={'fields':'id'})
        for field in proxy.fields:
            terms.append(SimpleVocabulary.createTerm(':' + field.id, None,
                                                     "%s (Custom)" % field.name))
    return SimpleVocabulary(terms)
