from collective.listingviews import LVMessageFactory as _
from zope.interface import Interface
from zope.schema import TextLine
from plone.z3cform.fieldsets import group as plonegroup
from z3c.form import form, field, group, button, interfaces
from plone.app.z3cform.layout import wrap_form
import zope.i18n
from zope import schema
from plone.directives import form
from five import grok
from z3c.form import button

from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

class IPerson(form.Schema):

    firstname = schema.TextLine(
        title=u"Firstname",
        required=True)

    lastname = schema.TextLine(
        title=u"Lastname",
        required=True)

    email = schema.TextLine(
        title=u"E-mail")

    address = schema.Text(
        title=u"Address")

class RegisterForm(form.SchemaForm):
    grok.name('register')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IPerson
    ignoreContext = True

    label = u"Register"
    description = u"After you will receive email to confirm registrations."

    def update(self):
        self.request.get('disable_border', True)
        super(RegisterForm, self).update()

    @button.buttonAndHandler(u"Register")
    def handleRegister(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErorrsMessage
            return

        self.context['Members'].invokeFactory('Person', **data)

        IStatusMessage(self.request).addStatusMessage(
            "Registered! Soon you will receive email.",
            'info')

        self.request.response.redirect(self.context.absolute_url())


ListingSettingsView = wrap_form(RegisterForm)
