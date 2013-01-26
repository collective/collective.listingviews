from plone.app.testing import PLONE_FIXTURE, PLONE_FUNCTIONAL_TESTING, PLONE_INTEGRATION_TESTING
from plone.app.testing import PloneSandboxLayer, FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


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

COLLECTIVE_LISTINGVIEWS_FIXTURE = CollectiveListingviews()
COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE, ),
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