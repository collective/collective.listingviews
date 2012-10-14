from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from utils import ComplexRecordsProxy
from interfaces import IListingCustomFieldControlPanel, IListingControlPanel
from zope.browsermenu import menu


def onRequest(context, request):
    # look up registry for views
    reg = queryUtility(IRegistry)
    if reg is not None:
        proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views':'id'})
        for view in proxy.views:
            terms.append(SimpleVocabulary.createTerm(view.id, view.id, view.name))
    # ensure our view ids are in the types
    # add adaptors for plone_displayviews for the menu items
            item = menu.BrowserMenuItem(IFolder, request)
            item.title = view.name
            item.action = view.id
    # register a more specific marker interface on siteroot so this doesn't get called again
