from collections import OrderedDict

from ZODB.POSException import ConflictError

try:
    from plone.namedfile.interfaces import IAvailableSizes
    getAllowedSizes = lambda: queryUtility(IAvailableSizes)()
except ImportError:
    from plone.app.imaging.utils import getAllowedSizes
from zope.interface import implements
from collective.listingviews.interfaces import IListingCustomFieldControlPanel, IListingControlPanel, ALL_TYPES
from collective.listingviews.utils import ComplexRecordsProxy, getRegistryFields
from z3c.formwidget.query.interfaces import IQuerySource
from zope.schema.interfaces import IContextSourceBinder, IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import queryUtility, getUtility, ComponentLookupError
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from collective.listingviews import LVMessageFactory as _
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

# LEAD_IMAGE_FIELD_ID = 'lead_image:tag_image'
# LEAD_IMAGE_FIELD_NAME = 'Lead Image (Virtual)'
# VIRTUAL_FIELDS = { LEAD_IMAGE_FIELD_ID:LEAD_IMAGE_FIELD_NAME }


class LVVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value
    This prevents any issues if a field
    is removed and the user had it selected.
    """

    def __init__(self, terms, *interfaces, **config):
        super(LVVocabulary, self).__init__(terms, *interfaces)
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
        except ConflictError:
            raise
        except:
            raise LookupError(value)


def ContentTypeVocabulary(context):
    """
    Vocabulary for all the content types
    """
    # http://developer.plone.org/content/types.html
    portal = getSite()
    # site_properties = getToolByName(portal, "portal_properties").site_properties
    # not_searched = site_properties.getProperty('types_not_searched', [])
    #
    # portal_types = getToolByName(portal, "portal_types")
    # types = portal_types.listContentTypes()
    #
    # # Get list of content type ids which are not filtered out
    # prepared_types = [t for t in types if t not in not_searched]
    # terms = [SimpleVocabulary.createTerm(id, None, portal_types[id].title) for id in prepared_types]
    # return SimpleVocabulary(terms)

    vocab = getUtility(IVocabularyFactory, name="plone.app.vocabularies.ReallyUserFriendlyTypes")
    all = SimpleVocabulary.createTerm(ALL_TYPES, None, _(u"All Types"))
    return SimpleVocabulary([all] + list(vocab(portal)))

def all_types():

    portal = getSite()
    vocab = getUtility(IVocabularyFactory, name="plone.app.vocabularies.ReallyUserFriendlyTypes")
    return [term.value for term in vocab(portal)]



def ListingViewVocabulary(context):
    terms = []
    reg = queryUtility(IRegistry)
    if reg is not None:
        proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views': 'id'})
        for view in proxy.views:
            terms.append(SimpleVocabulary.createTerm(view.id, view.id, view.name))
    return SimpleVocabulary(terms)

# TODO: Need to handle that date metadata changed names before 4->5 EffectiveDate -> effective. upgrade step?
BLACKLIST=['cmf_uid', 'in_response_to', 'sync_uid', 'Date', 'listCreators','getRemoteUrl', "UID", 'modified','created', 'effective', 'expires']
# TODO: should work out dynamically based on index type
DATE_INDEXES=['end', 'EffectiveDate', 'start', 'ExpirationDate', 'ModificationDate', 'CreationDate', 'modified','created', 'effective', 'expires', 'last_comment_date']

def MetadataVocabulary(context):
    """
    Metadata name is stored in registry. Format for default name is "fieldname:"
    and format for custom name is ":customname"
    """
    terms = []
    portal = getSite()
    values = dict()
    t = lambda d,v: SimpleVocabulary.createTerm(v, None, d)
    try:
        factory = getUtility(IVocabularyFactory, 'plone.app.contenttypes.metadatafields')
    except ComponentLookupError:
        factory = None
    try:
        tool = getToolByName(portal, 'portal_atct')
    except Exception:
        tool = None

    # Need to combine normal metadata vocab with our custom fields
    if factory is not None:
        # Plone 5
        metadataDisplay = OrderedDict()
        for term in factory(portal):
            metadataDisplay[term.value] = term.title
    elif tool is not None:
        # Plone 4
        metadataDisplay = getToolByName(portal, 'portal_atct').getMetadataDisplay()
    else:
        metadataDisplay = {}

    seen = {}

    for name, display_name in metadataDisplay.items():
        if name in BLACKLIST:
            continue
        # handle names that changed between plone versions
        name = dict(getId="id", Type="portal_type").get(name, name)
        if name in seen:
            continue

        display_name = unicode(display_name.replace('_', ' ').title())
        if name in DATE_INDEXES:
            display_name = dict(created=u"Creation", expires=u"Expiration", modified=u"Modification").get(name, display_name)
            display_name = display_name.replace(' Date','').replace('date','').capitalize()+' Date'
            for format,format_name in [('localshort', 'Date'),('locallong','Date & Time')]:
                terms.append(t("%s (%s)"%(display_name, format_name), "%s:%s"% (name, format), ))
        elif name in ['Title', 'id']:
            display_name = dict(id=u"Short Name").get(name, display_name)
            terms.append(t(display_name, name + ":", ))
            for format,format_name in [('tolink', 'Link')]:
                terms.append(t("%s (%s)" % (display_name, format_name),
                             "%s:%s"% (name, format), ))
        else:
            # TODO: better way to get consistent names
            display_name = dict(total_comments=u"Total number of comments",
                                Subject=u"Tags",
                                review_state=u"Review State",
                                Type=u"Portal Type",
                                getObjSize=u"Size",
                                getIcon=u"Icon",
                                UID=u"UID",
                                ).get(name, display_name)
            #display_name = display_name.title()
            terms.append(t(display_name, name + ":"))
        seen[name] = display_name

    # Lead image fields.
    # if getAvailableSizes is None:
    #     return self._sizes
    sizes = getAllowedSizes()

    for size in sizes:
        terms.append(t(u"Lead Image (%s)" % size, "lead_image:img_%s:tolink"%size))
    terms.append(t(u"Lead Image (Original)", "lead_image:img_image:tolink"))
    terms.append(t(u"Lead Image (URL)", "lead_image:"))
    # TODO: better display names

    # custom field
    for field in getRegistryFields().fields:
        terms.append(t("%s (Custom)" % field.name, ':' + field.id))
    return SimpleVocabulary(terms)

class VocabularySource(object):
     implements(IQuerySource)
     def __init__(self, vocabulary):
         self.vocabulary = vocabulary
     def __contains__(self, item):
         return self.vocabulary.__contains__(item)
     def __iter__(self):
         return self.vocabulary.__iter__()
     def getTerm(self):
         return self.vocabulary.getTerm()

     def getTermByToken(self):
        return self.vocabulary.getTermByToken()

     def search(self, query_string):
         return [v
                 for v in self
          if query_string.lower() in v.value.lower()]

class MetadataSourceBinder(object):
     implements(IContextSourceBinder)

     def __call__(self, context):
         return VocabularySource(MetadataVocabulary(context))
