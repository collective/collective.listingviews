from plone.app.testing import PLONE_FIXTURE, PLONE_FUNCTIONAL_TESTING, PLONE_INTEGRATION_TESTING
from plone.app.testing import PloneSandboxLayer, FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, setRoles, login
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD


class CollectiveListingviews(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.listingviews
        xmlconfig.file('configure.zcml',
                       collective.listingviews,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        applyProfile(portal, 'collective.listingviews:default')

class BrowserIntegrationTesting(IntegrationTesting):

    def setUpEnvironment(self, portal):
        super(BrowserIntegrationTesting, self).setUpEnvironment(portal)
        portal = self['portal']

        browser = Browser(portal)
        portalURL = portal.absolute_url()
        browser.open(portal.absolute_url()+'/@@listingviews_controlpanel')

        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()
        self['manager'] = browser

    def getFormFromControl(self, control):
        browser = self['manager']
        index = 0
        while True:
            try:
                form = browser.getForm(index=index)
            except:
                return None
            if form.mech_form == control.mech_form:
                return form
            else:
                index += 1
                continue






COLLECTIVE_LISTINGVIEWS_FIXTURE = CollectiveListingviews()
COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING = \
    BrowserIntegrationTesting(bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE, ),
                            name="CollectiveListingviews:Integration")

FIXTURE = CollectiveListingviews()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
    name='example.conference:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
    name='example.conference:Functional',
    )