from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
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
        applyProfile(portal, 'collective.listingviews:default')

COLLECTIVE_LISTINGVIEWS_FIXTURE = CollectiveListingviews()
COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE, ),
                       name="CollectiveListingviews:Integration")
