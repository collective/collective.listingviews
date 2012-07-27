from zope import interface, schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form
from collective.listingviews.interfaces import IListingSettings
from collective.listingviews.settings import ListingSettings
from collective.listingviews import LVMessageFactory as _
import zope.i18n


class MySchema(interface.Interface):
    age = schema.Int(title=u"Age")
    country = schema.Choice(title=(u"Country"), vocabulary="getpaid.countries", required=False, default=None)


class ListingSettingsForm(form.EditForm):
    fields = field.Fields(IListingSettings)

    label = _(u'heading_listing_settings_form', default=u'Listing Views Setting')
    description = _(u'description_listing_settings_form',
        default=u'Configure the parameters for this listing view.')

    successMessage = _(u'successMessage_listing_settings_form',
        default=u'Listing Settings Saved.')
    noChangesMessage = _(u'noChangesMessage_listing_settings_form',
        default=u'There are no changes in the Listing settings.')

    def update(self):
        super(ListingSettingsForm, self).update()

    def set_status_message(self, settings, has_changes):
        msg = has_changes and self.successMessage or self.noChangesMessage
        msg = zope.i18n.translate(msg)

        self.status = msg

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        settings = ListingSettings(self.context)

        has_changes = False
        if changes:
            settings = ListingSettings(self.context)
            settings.last_cooked_time_in_seconds = 0
            has_changes = True

        self.set_status_message(settings, has_changes)
        return self.request.response.redirect(self.context.absolute_url())


ListingSettingsView = wrap_form(ListingSettingsForm)
