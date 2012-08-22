from plone.app.registry.browser import controlpanel
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingControlSettings, IListingDefinition, IListingControlPanel
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility


class ListingControlPanel(object):
    implements(IListingControlPanel)


class ListingControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingControlPanel
    label = _(u"Listing view global settings")
    description = _(u"""""")

    def getContent(self):
        readonly = ListingControlPanel()
        #reg = getUtility(IRegistry)
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
        #reg = getUtility(IRegistry)
        reg = queryUtility(IRegistry)
        if reg is not None:
            facets = reg.collectionOfInterface(IListingDefinition, prefix='collective.listingviews.view')

            # remove indexes for unused fields
            #finally set the data in the registry
            i = 0
            for facet in data['views']:
                facets['view' + str(i)] = facet
                i += 1

            # remove any remaining fields
            for i in range(len(facets) - 1, len(data['views']) - 1, -1):
                #facet = facets['view' + str(i)]
                #name = facet.name
                #if type(name) == type(u''):
                #    name = name.encode('utf-8')
                #self.removeField(name)
                del facets['view' + str(i)]


class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingControlPanelForm
