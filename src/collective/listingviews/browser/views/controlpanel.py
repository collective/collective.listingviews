from collections import OrderedDict

from AccessControl import Permissions
from OFS.SimpleItem import SimpleItem
from Products.statusmessages.interfaces import IStatusMessage
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.registry.browser import controlpanel
from z3c.form.object import registerFactoryAdapter, FactoryAdapter
from zope.component.hooks import getSite
from zope.component.security import proxify
from zope.security.checker import Checker, CheckerPublic

from collective.listingviews import LVMessageFactory as _
from collective.listingviews.browser.tiles.contentlisting_tile import ContentListingTileView
from collective.listingviews.interfaces import (IListingControlSettings, IListingDefinition,
                                                IListingControlPanel, IListingCustomFieldControlPanel,
                                                ICustomFieldDefinition, ListingDefinition, IListingViewsBrowserLayer,
                                                ALL_TYPES)
from zope.interface import implements, alsoProvides, Interface
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.component import adapts, getUtility, getAdapters
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager
from zope.browser.interfaces import IBrowserView
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish, IContentish
from collective.listingviews.utils import ComplexRecordsProxy, getViewName, getRegistryViews, getRegistryFields, \
    NamedAdapterFactory
from five.customerize.zpt import TTWViewTemplate
from collective.listingviews.browser.views.listing_view import ListingView
from Products.CMFCore.utils import getToolByName
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.metaconfigure import addMenuItem, MenuItemFactory, menuItemDirective
from zope.browsermenu.menu import BrowserMenu, BrowserMenuItem, BrowserSubMenuItem
from zope.browsermenu.interfaces import IBrowserMenuItem
from plone.z3cform.crud import crud
from plone.z3cform import layout
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.autoform.form import AutoObjectSubForm, AutoFields, AutoExtensibleForm
from z3c.form import field, form, button
from zope.cachedescriptors.property import Lazy as lazy_property

from collective.listingviews.vocabularies import all_types

try:
    from plone.protect.interfaces import IDisableCSRFProtection
except ImportError:
    IDisableCSRFProtection = None
    # plone 4

try:
    from plone.app.standardtiles.contentlisting import IContentListingTileLayer
    MOSAIC = True
except ImportError:
    MOSAIC = False

class ProxyView(object):
    """Class to create simple proxy views."""

    def __init__(self, factory, checker):
        self.factory = factory
        self.checker = checker

    def __call__(self, *objects):
        return proxify(self.factory(*objects), self.checker)

def security_wrap_view(factory):
    #return factory

    checker = Checker(dict(__call__=CheckerPublic))  #TODO: should be Permissions.View I think but haven't got tests to work

    return ProxyView(factory, checker)


def addView(portal, data):
    views = getRegistryViews().views
    view = ListingDefinition(data)
    views.append(view)
    view_name = getViewName(view.id)
    syncViews(portal)
    return view_name

def updateView(portal, old_id, data):
    record = ListingDefinition(data)
    views = getRegistryViews().views
    views[views.indexof(old_id)] = record
    # assume view is already added
    syncViews(portal)
    return getViewName(record.id)



def sync_dicts(origin, target, add_func=None, del_func=None, mod_func=None):
    to_del = target.copy()

    for id, data in origin.items():
        if id not in to_del:
            if add_func is not None:
                add_func(id, data)
        else:
            if mod_func is not None:
                mod_func(id, data, to_del[id])
            del to_del[id]
    if del_func is not None:
        for id, data in to_del.items():
            del_func(id, data)



def syncViews(portal ):
    lsm = getSiteManager(portal)
    views = OrderedDict([(getViewName(view.id), view) for view in getRegistryViews().views if view.id and view.name])


    _registerMenuItems()


    # remove adapters registered in previous versions without the layer
    adapters = dict([(n,f) for n,f in lsm.adapters.lookupAll((IContentish, IBrowserRequest), IBrowserView) if n.startswith('collective.listingviews.')])
    def removeView(name, factory):
        assert lsm.unregisterAdapter(required=(IContentish, IBrowserRequest),
                             provided=IBrowserView,
                             name=name)
    sync_dicts(dict(), adapters, None, removeView)

    # browser views
    adapters = dict([(n,f) for n,f in lsm.adapters.lookupAll((IContentish, IListingViewsBrowserLayer), IBrowserView) if n.startswith('collective.listingviews.')])
    def addView(name, _):
        # TODO: should really only be registered against the types that were chosen or their Interfaces
        lsm.registerAdapter(NamedAdapterFactory(name, ListingView),
                           required=(IContentish, IListingViewsBrowserLayer),
                           provided=IBrowserView,
                           name=name)
    def removeView(name, _):
        assert lsm.unregisterAdapter(required=(IContentish, IListingViewsBrowserLayer),
                             provided=IBrowserView,
                             name=name)

    sync_dicts(views, adapters, addView, removeView)


    # fti
    portal_types = getToolByName(portal, "portal_types")

    ftis = dict([(name,fti) for fti in portal_types.listTypeInfo() for name in getattr(fti, 'view_methods', []) if name.startswith('collective.listingviews.')])
    def add_fti(name, view):
        types = all_types() if ALL_TYPES in view.restricted_to_types else view.restricted_to_types
        for type_ in types:
            fti = portal_types.getTypeInfo(type_)
            if getattr(fti, 'view_methods', None) is None:
                # raise Exception("No dynamic view enabled for %s"%type_)
                # TODO we need to warn user that only portlets will work for this type
                continue
            if name not in fti.view_methods:
                fti.manage_changeProperties(view_methods=fti.view_methods + (name,))

    def del_fti(name, fti):
        fti.manage_changeProperties(view_methods=tuple(m for m in fti.view_methods if m != name))

    sync_dicts(views, ftis, add_fti, del_fti)

    # Tiles
    stlisting_views = getUtility(IRegistry).get('plone.app.standardtiles.listing_views', None)
    if stlisting_views is None:
        return

    changed = False
    def add_lv(name, view):
        stlisting_views[unicode(name)] = unicode(view.name)
        changed = True
    def del_lv(name, title):
        if name.startswith("collective.listingviews."):
            del stlisting_views[unicode(name)]
            changed = True
    def mod_lv(name, view, lvtitle):
        if lvtitle != unicode(view.name):
            stlisting_views[unicode(name)] = unicode(view.name)
            changed = True
    sync_dicts(views, stlisting_views, add_lv, del_lv, mod_lv)
    if changed:
        getUtility(IRegistry)['plone.app.standardtiles.listing_views'] = stlisting_views

    # TODO: make sure this is only in our layer
    adapters = dict([(n,f) for n,f in lsm.adapters.lookupAll((Interface, IContentListingTileLayer), IBrowserView) if n.startswith('collective.listingviews.')])
    def add_tile(name, view):
        lsm.registerAdapter(NamedAdapterFactory(name, ContentListingTileView),
                           required=(Interface, IContentListingTileLayer),
                           provided=IBrowserView,
                           name=name)
    def del_tile(name, _):
        assert lsm.unregisterAdapter(
                           required=(Interface, IContentListingTileLayer),
                           provided=IBrowserView,
                           name=name)
    sync_dicts(views, adapters, add_tile, del_tile)

# We need to register our menuitems the first time it's accessed per thread as we can't use local site manager
# called from zope.app.publication.interfaces.IBeforeTraverseEvent
def registerMenuItems(site, event, _handled=set()):
    if site.getPhysicalPath() not in _handled:
        _registerMenuItems()
        _handled.add(site.getPhysicalPath())


def _registerMenuItems():

    views = OrderedDict([(getViewName(view.id), view) for view in getRegistryViews().views if view.id and view.name])

    gsm = getGlobalSiteManager()
    menu = getUtility(IBrowserMenu, 'plone_displayviews')
    adapters = dict([(n,f) for n,f in gsm.adapters.lookupAll((IContentish, IListingViewsBrowserLayer), menu.getMenuItemType()) if n.startswith('collective.listingviews.')])
    def del_submenu(name, _):
        gsm.unregisterAdapter(
            required=(IContentish, IListingViewsBrowserLayer),
            provided=menu.getMenuItemType(),
            name=name,
        )

    def add_submenu(name, view):
        factory = security_wrap_view(MenuItemFactory(
            BrowserMenuItem,
            title=view.name,
            action=name,
            description=view.name,
#            permission="cmf.ModifyViewTemplate",
            permission=CheckerPublic,  # To satisfy test. Menu should be hidden anyway
            # icon=icon,
            #filter=filter, permission=permission, extra=extra, order=order,
    #                    _for=(IContentish, IDefaultBrowserLayer)
            )
        )

        gsm.registerAdapter(
            factory,
            required=(IContentish, IListingViewsBrowserLayer),
            provided=menu.getMenuItemType(),
            name=name,
        )
    def mod_submenu(name, view, factory):
        menu = factory(None, None)
        if view.name != menu.title:
            del_submenu(name, factory)
            add_submenu(name, view)
    sync_dicts(views, adapters, add_submenu, del_submenu, mod_submenu)



# plone.z3cform.crud based implementation

class ListingViewDefinitionEditForm(AutoExtensibleForm, crud.EditSubForm):
    @property
    def schema(self):
        return self.context.context.update_schema

class ListingViewEditForm(crud.EditForm):

#    label = None

#    buttons = crud.EditForm.buttons.copy().omit('edit')
    handlers = crud.EditForm.handlers.copy()
    editsubform_factory = ListingViewDefinitionEditForm

class ListingViewAddForm(AutoExtensibleForm, crud.AddForm,):
    @property
    def schema(self):
        schema =  self.context.add_schema
        return schema

    # @property
    # def fields(self):
    #     # TODO: better to handle this as a "All Types" item to select since new types can be added later
    #     fields = field.Fields(self.context.add_schema)
    #     #Override to select all types
    #     fields['restricted_to_types'].field.default = all_types()
    #     return fields

    # fixes bug with OrderedSelect widget which turns crud-add.form into crud.add.form
    prefix = 'crud.add.form.'


    @button.buttonAndHandler(_(u'Edit Custom Fields'), name="redirectCustomFields")
    def handleRedirectCustomFields(self, action):
        url = u"{0}/@@listingviewfields_controlpanel".format(getSite().absolute_url())
        self.request.response.redirect(url)

class ListingViewSchemaListing(crud.CrudForm):
    """ The combined pigeonhole edit + add forms.
    """

    @lazy_property
    def description(self):
        if self.get_items():
            return _(u'The following custom listing views are available for '
                     u'your site.')
        else:
            return _(u'Click the "Add" button to begin creating '
                     u' a new listing view.')

    #update_schema = field.Fields(IListingDefinition).select('name')
    view_schema = field.Fields(IListingDefinition).select('id', 'item_fields','listing_fields')
    #add_schema = field.Fields(IListingDefinition).select('id', 'name')
    add_schema = IListingDefinition
    addform_factory = ListingViewAddForm
#    editform_factory = ListingViewEditForm

    ignoreContext = True

    def get_items(self):
        """ Look up all existing views in the registry.
        """
        return [(v.id, v) for v in getRegistryViews().views if v.id]

    def add(self, data):
        addView(self.context, data)

    def remove(self, (name, item)):
        """ Remove a schema.
        """
        views = getRegistryViews().views
        view = views.get(name)
        del views[views.indexof(name)]
        syncViews(self.context)
        _registerMenuItems()

    def link(self, item, field):
        """ Generate links to the edit page for each schema.
        """
        if field == 'id':
            return '%s/%s' % (self.context.absolute_url(), item.id)

ListingViewSchemaListingView = layout.wrap_form(ListingViewSchemaListing, ControlPanelFormWrapper)
ListingViewSchemaListingView.label = u"Listing Views"



class ListingViewEditForm(controlpanel.RegistryEditForm):

    schema = IListingDefinition
    label = _(u"Edit Listing View")
    description = _(u"""""")

    #Override so save and cancel work
    control_panel_view = ""

    def getContent(self):
        id = self.context.__name__
        view = getRegistryViews().views.get(id)
        return view

    def applyChanges(self, data):
        # for each view we will create a new view in customerize and add that as a menu
        # item in the display menu
        id = self.context.__name__
        updateView(self.context, id, data)

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        url = u"{0}/@@listingviews_controlpanel".format(getSite().absolute_url())
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        url = u"{0}/@@listingviews_controlpanel".format(getSite().absolute_url())
        self.request.response.redirect(url)


class ListingViewEditFormConfiglet(controlpanel.ControlPanelFormWrapper):
    form = ListingViewEditForm



class ListingViewControlPanel(SimpleItem):
    """ This class represents the Pigeonhole configlet, and allows us to traverse
        through it to (a wrapper of) a particular schema.
    """
    implements(IBrowserPublisher)

    def __init__(self, context, request):
        super(ListingViewControlPanel, self).__init__(context, request)

        # make sure that breadcrumbs will be correct
        self.id = None
        self.Title = lambda: _(u'Listing Views')

        # #TODO: find out why this view does a write on read
        # if IDisableCSRFProtection is not None:
        #     alsoProvides(request, IDisableCSRFProtection)


    def publishTraverse(self, request, name):
        """ Use another context for breadcrumbs
        """
        # disable inline validation as it doesn't work
        if name == 'kss_z3cform_inline_validation':
            return
        return ListingViewEditContext(self.context, request, name).__of__(self)

    def browserDefault(self, request):
        """ If we aren't traversing to a schema beneath the types configlet, we actually want to
            see the PigeonholeSchemaListing.
        """
        return self, ('@@contents',)

class ListingViewEditContext(SimpleItem):
    # Implementing IBrowserPublisher tells the Zope 2 publish traverser to pay attention
    # to the publishTraverse and browserDefault methods.
    implements(IBrowserPublisher)


    def __init__(self, context, request, name=u'schema', title=None):
        super(ListingViewEditContext, self).__init__(context, request)
        self.context = context
        self.request = request

        # make sure absolute_url and breadcrumbs are correct
        #self.id = None
        self.__name__ = name
        if title is None:
            title = name
        self.Title = lambda: title

    def publishTraverse(self, request, name):
        """ Look up the field whose name matches the next URL path element, and wrap it.
        """
        return DefaultPublishTraverse(self, request).publishTraverse(request, name)

    def browserDefault(self, request):
        """ If not traversing through the schema to a field, show the SchemaListingPage.
        """
        return self, ('@@edit',)


class ListingCustomFieldControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingCustomFieldControlPanel
    label = _(u"Manage Custom Listing Fields")
    description = _(u"""""")

    def getContent(self):
        #TODO: find out why this view does a write on read
        #alsoProvides(self.request, IDisableCSRFProtection)

        return getRegistryFields()
#
#    def updateWidgets(self):
#        super(ListingCustomFieldControlPanelForm, self).updateWidgets()
#        import pdb; pdb.set_trace()
#        self.widgets['tal_statement'].size = 100

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        url = u"{0}/@@listingviews_controlpanel".format(getSite().absolute_url())
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        url = u"{0}/@@listingviews_controlpanel".format(getSite().absolute_url())
        self.request.response.redirect(url)


class ListingCustomFieldControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingCustomFieldControlPanelForm

