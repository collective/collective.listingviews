from plone.app.registry.browser import controlpanel
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingControlSettings, IListingDefinition,\
    IListingControlPanel, IListingCustomFieldControlPanel, ICustomFieldDefinition
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.component import adapts, getUtility, getAdapters
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager
from zope.browser.interfaces import IBrowserView
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish, IContentish
from collective.listingviews.utils import ComplexRecordsProxy
from five.customerize.zpt import TTWViewTemplate
from collective.listingviews.browser.views.listing_view import ListingView
from Products.CMFCore.utils import getToolByName
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.metaconfigure import addMenuItem, MenuItemFactory, menuItemDirective
from zope.browsermenu.menu import BrowserMenu, BrowserMenuItem, BrowserSubMenuItem
from zope.browsermenu.interfaces import IBrowserMenuItem
from Products.ATContentTypes.permission import ModifyViewTemplate


class ListingControlPanel(object):
    implements(IListingControlPanel)


def getViewName(view_id):
    return 'collective.listingviews.%s'%view_id

def getRegistryViews():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views':'id'})
    return proxy


class ListingControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingControlPanel
    label = _(u"Manage Listing Views")
    description = _(u"""""")

    def getContent(self):
        return getRegistryViews()

    def applyChanges(self, data):
        import pdb; pdb.set_trace()
        # for each view we will create a new view in customerize and add that as a menu
        # item in the display menu
        sm = getSiteManager(self.context)

        portal_types = getToolByName(self.context, "portal_types")

        old_views = set([view.id for view in getRegistryViews().views])

        for view in data['views']:
            view_name = getViewName(view.id)
            sm.registerAdapter(ListingView,
                               required=(IFolderish, IBrowserRequest),
                               provided=IBrowserView,
                               name=view_name)

            # add view to the relevent types
            for type_ in ['Folder', 'Topic']:
                fti = portal_types.getTypeInfo(type_)
                if view_name not in fti.view_methods:
                    fti.manage_changeProperties(view_methods=fti.view_methods+(view_name,))

            # registering a menu item will be done in beforeSiteTraverse event

            if view.id in old_views:
                old_views.remove(view.id)

        for view_id in old_views:
            view_name = getViewName(view)
            sm.unregisterAdapter(required = (IFolderish, IBrowserRequest),
                               provided = IBrowserView,
                               name = view_name)


        # registering a menu item will be done in beforeSiteTraverse event
        #TODO unregister any old views
        super(ListingControlPanelForm, self).applyChanges(data)

        # register all the menu names again from registery
        _registerMenuItems()


# We need to register our menuitems the first time it's accessed
def registerMenuItems(site, event, _handled=set()):
    if site.getPhysicalPath() not in _handled:
        _registerMenuItems()
        _handled.add(site.getPhysicalPath())


def _registerMenuItems():

    proxy = getRegistryViews()
    gsm = getGlobalSiteManager()
    menu = getUtility(IBrowserMenu, 'plone_displayviews')
    for view in proxy.views:
        # register a menu item
        view_name = getViewName(view.id)
        factory = MenuItemFactory(
            BrowserMenuItem,
            title=view.name,
            action=view_name,
            #description=description,
            # icon=icon,
            #filter=filter, permission=permission, extra=extra, order=order,
    #                    _for=(IContentish, IDefaultBrowserLayer)
            )
        # ensure we remove our old factory if already registered
        gsm.unregisterAdapter(
            required=(IFolderish, IDefaultBrowserLayer),
            provided=menu.getMenuItemType(),
            name=view.name,
        )

        gsm.registerAdapter(
            factory,
            required=(IFolderish, IDefaultBrowserLayer),
            provided=menu.getMenuItemType(),
            name=view.name,
        )


        #assert menu.getMenuItemByAction(IFolderish, self.request, view_name)
        # pp [x for x in gsm.registeredAdapters() if x.provided == menu.getMenuItemType()]


class ListingCustomFieldControlPanel(object):
    implements(IListingCustomFieldControlPanel)


class ListingCustomFieldControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingCustomFieldControlPanel
    label = _(u"Manage Custom Listing Fields")
    description = _(u"""""")

    def getContent(self):
        reg = queryUtility(IRegistry)
        return ComplexRecordsProxy(reg, IListingCustomFieldControlPanel,
                                   prefix='collective.listingviews.customfield',
                                   key_names={'fields': 'id'})


class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingControlPanelForm


class ListingCustomFieldControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingCustomFieldControlPanelForm
