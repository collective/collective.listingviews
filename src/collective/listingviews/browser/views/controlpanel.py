from plone.app.registry.browser import controlpanel
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingControlSettings, IListingDefinition,\
    IListingControlPanel, IListingCustomFieldControlPanel, ICustomFieldDefinition
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility


class ListingControlPanel(object):
    implements(IListingControlPanel)


class ListingControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingControlPanel
    label = _(u"Manage Listing Views")
    description = _(u"""""")

    def getContent(self):
        readonly = ListingControlPanel()
        reg = queryUtility(IRegistry)
        if reg is not None:
            # copy non-collection settings
            data = reg.forInterface(IListingControlSettings, prefix='collective.listingviews')
            for name in data.__schema__:
                setattr(readonly, name, getattr(data, name))
            # switch out facet data for that from the registry
            facets = sorted(reg.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view').items())
            readonly.views = [facet for _, facet in facets]
        return readonly

    def applyChanges(self, data):
        reg = queryUtility(IRegistry)
        if reg is not None:
            facets = reg.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view')

            # remove indexes for unused fields
            # finally set the data in the registry
            i = 0
            for facet in data['views']:
                facets['view' + str(i)] = facet
                i += 1

            # remove any remaining fields
            for i in range(len(facets) - 1, len(data['views']) - 1, -1):
                del facets['view' + str(i)]


class ListingCustomFieldControlPanel(object):
    implements(IListingCustomFieldControlPanel)


class ListingCustomFieldControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingCustomFieldControlPanel
    label = _(u"Manage Custom Listing Fields")
    description = _(u"""""")

    def getContent(self):
        readonly = ListingCustomFieldControlPanel()
        reg = queryUtility(IRegistry)
        if reg is not None:
            # copy non-collection settings
            data = reg.forInterface(IListingControlSettings, prefix='collective.listingviews')
            for name in data.__schema__:
                setattr(readonly, name, getattr(data, name))
            # switch out facet data for that from the registry
            facets = sorted(reg.collectionOfInterface(ICustomFieldDefinition, prefix='collective.listingviews.customfield').items())
            readonly.fields = [facet for _, facet in facets]
        return readonly

    def applyChanges(self, data):
        reg = queryUtility(IRegistry)
        if reg is not None:
            facets = reg.collectionOfInterface(ICustomFieldDefinition, prefix='collective.listingviews.customfield')

            # remove indexes for unused fields
            # finally set the data in the registry
            i = 0
            for facet in data['fields']:
                facets['field' + str(i)] = facet
                i += 1

            # remove any remaining fields
            for i in range(len(facets) - 1, len(data['fields']) - 1, -1):
                del facets['field' + str(i)]


class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingControlPanelForm


class ListingCustomFieldControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingCustomFieldControlPanelForm
