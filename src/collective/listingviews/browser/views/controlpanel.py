from plone.app.registry.browser import controlpanel
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingControlSettings, IListingDefinition,\
    IListingControlPanel, IListingCustomFieldControlPanel, ICustomFieldDefinition
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.component import adapts, getUtility
from collective.listingviews.utils import ComplexRecordsProxy

class ListingControlPanel(object):
    implements(IListingControlPanel)


class ListingControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingControlPanel
    label = _(u"Manage Listing Views")
    description = _(u"""""")

    def getContent(self):
        reg = getUtility(IRegistry)
        proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                    key_names={'views':'id'})
        return proxy


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
                                   key_names={'fields':'id'})


class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingControlPanelForm


class ListingCustomFieldControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingCustomFieldControlPanelForm
