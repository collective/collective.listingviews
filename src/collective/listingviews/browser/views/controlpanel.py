from plone.app.registry.browser import controlpanel
from collective.listingviews import LVMessageFactory as _
from collective.listingviews.interfaces import IListingControlPanel


class ListingControlPanelForm(controlpanel.RegistryEditForm):

    schema = IListingControlPanel
    label = _(u"Listing view global settings")
    description = _(u"""""")

    def updateFields(self):
        super(ListingControlPanelForm, self).updateFields()

    def updateWidgets(self):
        super(ListingControlPanelForm, self).updateWidgets()


class ListingControlPanelView(controlpanel.ControlPanelFormWrapper):
    form = ListingControlPanelForm
