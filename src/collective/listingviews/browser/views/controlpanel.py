from OFS.SimpleItem import SimpleItem
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.registry.browser import controlpanel

from collective.listingviews import LVMessageFactory as _
from collective.listingviews.browser.tiles.contentlisting_tile import ContentListingTileView
from collective.listingviews.interfaces import (IListingControlSettings, IListingDefinition,
    IListingControlPanel, IListingCustomFieldControlPanel, ICustomFieldDefinition, all_types)
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
from collective.listingviews.utils import ComplexRecordsProxy
from five.customerize.zpt import TTWViewTemplate
from collective.listingviews.browser.views.listing_view import ListingView
from Products.CMFCore.utils import getToolByName
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.metaconfigure import addMenuItem, MenuItemFactory, menuItemDirective
from zope.browsermenu.menu import BrowserMenu, BrowserMenuItem, BrowserSubMenuItem
from zope.browsermenu.interfaces import IBrowserMenuItem
from Products.ATContentTypes.permission import ModifyViewTemplate
from plone.z3cform.crud import crud
from plone.z3cform import layout
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.autoform.form import AutoObjectSubForm, AutoFields, AutoExtensibleForm
from z3c.form import field, form, button
from zope.cachedescriptors.property import Lazy as lazy_property
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

def getViewName(view_id):
    return 'collective.listingviews.%s'%view_id

def getListingNameFromView(view_name):
    #TODO beter way then replace, could appear in the middle.
    return view_name.replace('collective.listingviews.', '')


def getRegistryViews():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views':'id'})
    return proxy

def getRegistryFields():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IListingCustomFieldControlPanel,
                                   prefix='collective.listingviews.customfield',
                                   key_names={'fields': 'id'})
    return proxy


def addView(portal, view):
    view_name = getViewName(view.id)
    sm = getSiteManager(portal)
    sm.registerAdapter(ListingView,
                       required=(IContentish, IBrowserRequest),
                       provided=IBrowserView,
                       name=view_name)
    portal_types = getToolByName(portal, "portal_types")

    # add view to the relevent types
    for type_ in view.restricted_to_types:
        fti = portal_types.getTypeInfo(type_)
        if getattr(fti,'view_methods',None) is None:
            #raise Exception("No dynamic view enabled for %s"%type_)
            #TODO we need to warn user that only portlets will work for this type
            continue
        if view_name not in fti.view_methods:
            fti.manage_changeProperties(view_methods=fti.view_methods+(view_name,))

    # Register the view also for tiles if standardtiles is installed
    registry = getUtility(IRegistry)
    stlisting_views = registry.get('plone.app.standardtiles.listing_views', None)
    if stlisting_views is not None:
        # Adapter the various listing views in the content listing tile
        sm.registerAdapter(ContentListingTileView,
                           required=(Interface, IContentListingTileLayer),
                           provided=IBrowserView,
                           name=view_name)
        if view_name not in stlisting_views:
            stlisting_views[view_name] = unicode(view.name)



def removeView(portal, view):
    view_name = getViewName(view.id)
    sm = getSiteManager(portal)
    sm.unregisterAdapter(required = (IContentish, IBrowserRequest),
                       provided = IBrowserView,
                       name = view_name)
    registry = getUtility(IRegistry)
    stlisting_views = registry.get('plone.app.standardtiles.listing_views', None)
    if stlisting_views is not None:
        sm.unregisterAdapter(ListingView,
                           required=(IContentish, IContentListingTileLayer),
                           provided=IBrowserView,
                           name=view_name)
        if view_name in stlisting_views:
            del stlisting_views[view_name]


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
        if not view.id or not view.name:
            #TODO: should give a warning
            continue
        # register a menu item
        view_name = getViewName(view.id)
        factory = MenuItemFactory(
            BrowserMenuItem,
            title=view.name,
            action=view_name,
            description=view.name,
            # icon=icon,
            #filter=filter, permission=permission, extra=extra, order=order,
    #                    _for=(IContentish, IDefaultBrowserLayer)
            )
        # ensure we remove our old factory if already registered
        gsm.unregisterAdapter(
            required=(IContentish, IDefaultBrowserLayer),
            provided=menu.getMenuItemType(),
            name=view_name,
        )

        gsm.registerAdapter(
            factory,
            required=(IContentish, IDefaultBrowserLayer),
            provided=menu.getMenuItemType(),
            name=view_name,
        )


        #assert menu.getMenuItemByAction(IFolderish, self.request, view_name)
        # pp [x for x in gsm.registeredAdapters() if x.provided == menu.getMenuItemType()]


class ListingDefinition(object):
    implements(IListingDefinition)

    def __init__(self, data):
        for key,value in data.items():
            setattr(self, key, value)



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

class ListingViewAddForm(crud.AddForm, AutoExtensibleForm):
    @property
    def schema(self):
        schema =  self.context.add_schema
        return schema

    @property
    def fields(self):
        fields = field.Fields(self.context.add_schema)
        #Override to select all types
        fields['restricted_to_types'].field.default = all_types()
        return fields

    # fixes bug with OrderedSelect widget which turns crud-add.form into crud.add.form
    prefix = 'crud.add.form.'

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

    update_schema = field.Fields(IListingDefinition).select('name')
    view_schema = field.Fields(IListingDefinition).select('id')
    add_schema = IListingDefinition
    addform_factory = ListingViewAddForm
#    editform_factory = ListingViewEditForm

    ignoreContext = True

    def get_items(self):
        """ Look up all existing views in the registry.
        """
        return [(v.id, v) for v in getRegistryViews().views if v.id]

    def add(self, data):
        views = getRegistryViews().views
        record = ListingDefinition(data)
        views.append(record)
        addView(self.context, record)
        _registerMenuItems()

    def remove(self, (name, item)):
        """ Remove a schema.
        """
        views = getRegistryViews().views
        view = views.get(name)
        del views[views.indexof(name)]
        removeView(self.context, view)
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
        record = ListingDefinition(data)
        views = getRegistryViews().views
        views[views.indexof(id)] = record
        # assume view is already added
        _registerMenuItems()


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

        #TODO: find out why this view does a write on read
        if IDisableCSRFProtection is not None:
            alsoProvides(request, IDisableCSRFProtection)


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


# Old crud form

#class ListingControlPanelForm(controlpanel.RegistryEditForm):
#
#    schema = IListingControlPanel
#    label = _(u"Manage Listing Views")
#    description = _(u"""""")
#
#    def getContent(self):
#        return getRegistryViews()
#
#    def applyChanges(self, data):
#        #import pdb; pdb.set_trace()
#        # for each view we will create a new view in customerize and add that as a menu
#        # item in the display menu
#
#        old_views = set([view.id for view in getRegistryViews().views])
#
#        for view in data['views']:
#            addView(self.context, view)
#            # registering a menu item will be done in beforeSiteTraverse event
#            if view.id in old_views:
#                old_views.remove(view.id)
#
#        for view_id in old_views:
#            removeView(self.context, view)
#
#
#        # registering a menu item will be done in beforeSiteTraverse event
#        #TODO unregister any old views
#        super(ListingControlPanelForm, self).applyChanges(data)
#
#        # register all the menu names again from registery
#        _registerMenuItems()
#
#class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
#    form = ListingControlPanelForm

#class ListingCustomFieldControlPanel(object):
#    implements(IListingCustomFieldControlPanel)
#class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
#    form = ListingControlPanelForm


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
        


class ListingCustomFieldControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingCustomFieldControlPanelForm
