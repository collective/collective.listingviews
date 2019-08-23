import unittest2 as unittest
from z3c.form.interfaces import IObjectFactory
from zope.component import getMultiAdapter
from zope.interface import Interface

from collective.listingviews.browser.views.controlpanel import addView, CustomFieldDefinition

from Products.CMFCore.utils import getToolByName

from collective.listingviews.testing import\
    COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING
from collective.listingviews.utils import getRegistryFields
from collective.listingviews.vocabularies import MetadataVocabulary




class TestRegistration(unittest.TestCase):

    layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.maxDiff = 1000

    def test_product_is_installed(self):
        """
        Validate that our products GS profile has been run and the product
        installed
        """
        pid = 'collective.listingviews'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_fields_vocabulary(self):
        self.assertItemsEqual([u'Creator',
                               u'Creation Date (Date & Time)',
                               u'Creation Date (Date)',
                               u'Description',
                               u'Effective Date (Date & Time)',
                               u'Effective Date (Date)',
                               u'End Date (Date & Time)',
                               u'End Date (Date)',
                               u'Expiration Date (Date & Time)',
                               u'Expiration Date (Date)',
                               u'Location',
                               u'Modification Date (Date & Time)',
                               u'Modification Date (Date)',
                               u'Short Name',
                               u'Short Name (Link)',
                               u'Size',
                               u'Start Date (Date & Time)',
                               u'Start Date (Date)',
                               u'State',
                               u'Tags',
                               u'Title',
                               u'Title (Link)',
                               u'Total number of comments'],
            [t.title for t in MetadataVocabulary(self.portal)]
            )
        self.assertItemsEqual(
                              ['Creator:',
                               'Description:',
                               'end:locallong',
                               'end:localshort',
                               'CreationDate:locallong',
                               'CreationDate:localshort',
                               'EffectiveDate:locallong',
                               'EffectiveDate:localshort',
                               'ExpirationDate:locallong',
                               'ExpirationDate:localshort',
                               'ModificationDate:locallong',
                               'ModificationDate:localshort',
                               'location:',
                               'getId:',
                               'getId:tolink',
                               'getObjSize:',
                               'start:locallong',
                               'start:localshort',
                               'review_state:',
                               'Subject:',
                               'Title:',
                               'Title:tolink',
                               'total_comments:'],
            [t.value for t in MetadataVocabulary(self.portal)],
            )


    def test_listing_date_localshort(self):

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["EffectiveDate:localshort"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'Dec 31, 2000', )

    def test_item_date_locallong(self):

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=["EffectiveDate:locallong"],
            listing_fields=[],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.item1.unrestrictedTraverse("@@" + view)()
        self.assertRegexpMatches(body, 'Jan 01, 2001 12:00 AM', )

        # TODO: test other dates

    def test_add_custom_field(self):

        fields = getRegistryFields().fields
        # factory = getMultiAdapter( (Interface, Interface, Interface, Interface), IObjectFactory,
        #                           name="collective.listingviews.interfaces.ICustomFieldDefinition")

        record = CustomFieldDefinition(
            id="myfield",
            name="My Field",
            tal_statement="python: 'hello world'"
        )
        fields.append(record)

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=[":myfield"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'hello world', )
