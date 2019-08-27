import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from collective.listingviews.browser.views.controlpanel import addView
from collective.listingviews.interfaces import CustomFieldDefinition
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
        self.maxDiff = 2000

    def assertItemsSubset(self, items, all_items):
        for i in items:
            self.assertIn(i, all_items)

    def test_fields_vocabulary(self):
        # TODO: backport 5.1 fields so vocab is equal on all verisons
        self.assertItemsSubset([u'Creator',
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
                               u'Review State',
                               u'Tags',
                               u'Title',
                               u'Title (Link)',
                               u'Total number of comments'],
            [t.title for t in MetadataVocabulary(self.portal)]
            )
        self.assertItemsSubset(
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


    def test_collection_date_localshort(self):

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["EffectiveDate:localshort"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'Dec 31, 2000', )

    def test_folder_date_localshort(self):

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["EffectiveDate:localshort"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.unrestrictedTraverse("@@"+view)()
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

    # TODO: other fields

    # TODO: other content types

    def test_add_custom_field(self):

        fields = getRegistryFields().fields
        # factory = getMultiAdapter( (Interface, Interface, Interface, Interface), IObjectFactory,
        #                           name="collective.listingviews.interfaces.ICustomFieldDefinition")

        record = CustomFieldDefinition(dict(
            id="myfield",
            name="My Field",
            tal_statement="python: 'hello world'"
        ))
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

    def test_sortable_collections(self):
        " We need to test sorting in collections? "
        tal = "python:modules['DateTime.DateTime'](path('item/EffectiveDate')).strftime('%d/%m/%Y') if path('item/EffectiveDate') != 'None' else '' "
        record = CustomFieldDefinition(dict(
            id="pubdate2",
            name="My Field",
            tal_statement=tal
        ))
        getRegistryFields().fields.append(record)

        view = addView(self.portal, dict(
            id="pubnews2",
            name="News with publication",
            item_fields=['Title:'],
            listing_fields=[":pubdate2"],
            restricted_to_types=['Page', 'Folder', 'Collection']
        ))

        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        #self.assertRegexpMatches(body, '(?m)31/12/2000.*01/01/2001')
        self.assertGreater(body.index("01/01/2001"), body.index("31/12/2000"))
