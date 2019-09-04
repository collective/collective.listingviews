import unittest2 as unittest
from AccessControl.security import newInteraction
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login, TEST_USER_NAME, SITE_OWNER_NAME, setRoles, TEST_USER_ID
#from plone.z3cform.tests import TestRequest
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility, queryAdapter, getAdapters, getSiteManager, getGlobalSiteManager
from zope.globalrequest import getRequest, setRequest
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IVocabularyFactory
import re
from zope.security._definitions import thread_local
from collective.listingviews.browser.views.controlpanel import addView, updateView
from collective.listingviews.interfaces import CustomFieldDefinition
from collective.listingviews.testing import \
    COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING, COLLECTIVE_LISTINGVIEWS_FUNCTIONAL_TESTING
from collective.listingviews.utils import getRegistryFields, getRegistryViews
from collective.listingviews import plone_version
PLONE5 = plone_version >= "5"


class TestRegistration(unittest.TestCase):

    layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.maxDiff = 2000


        # Need some extra request vars
        if self.portal.REQUEST is not None:
            request = self.portal.REQUEST
        else:
            request = getRequest()
        if request is None:
            request = TestRequest()
        setRequest(request)

        #directlyProvides(getRequest(), IDefaultBrowserLayer)
        for dummy in ['ACTUAL_URL', 'URL']:
            request.form.setdefault(dummy, 'dummy')

        # Not sure why this is needed but single test to test menu items checkpermission needs this
        try:
            interaction = thread_local.interaction
        except AttributeError:
            newInteraction()

        #login(self.portal, SITE_OWNER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        delattr(thread_local, 'interaction')


    def assertItemsSubset(self, items, all_items):
        for i in items:
            self.assertIn(i, all_items)



    def test_types_vocabulary(self):
        factory = getUtility(IVocabularyFactory, 'plone.app.vocabularies.ReallyUserFriendlyTypes')
        #factory = getUtility(IVocabularyFactory, 'collective.listingviews.ContentTypeVocabulary')
        vocabulary = factory(self.portal)
        self.assertItemsSubset([u'Collection',
                               u'Comment',
                               u'Event',
                               u'File',
                               u'Folder',
                               u'Image',
                               u'Link',
                               u'News Item',
                               u'Page'],
                               [t.title for t in vocabulary]
                               )
        self.assertItemsSubset(['Discussion Item',
                               'Event',
                               'File',
                               'Folder',
                               'Image',
                               'Link',
                               'News Item',
                               'Document'],
                               [t.value for t in vocabulary]
                               )

    def test_fields_vocabulary(self):
        factory = getUtility(IVocabularyFactory, 'collective.listingviews.MetadataVocabulary')
        vocabulary = factory(self.portal)
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
            [t.title for t in vocabulary]
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
            [t.value for t in vocabulary],
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

        record = CustomFieldDefinition(dict(
            id="myfield",
            name="My Field",
            tal_statement="python: 'hello world'"
        ))
        getRegistryFields().fields.append(record)

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=[":myfield"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'hello world', 'Custom field not found')


    def test_add_virtual_field(self):

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["lead_image:tag_image"],
            restricted_to_types=[]
        ))
        fudgeRequest()
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        regexp = '(.*)<dd class="listing-field field-lead_image-tag_image">(.*)<img src="http://nohost/plone/(.*)" alt="(.*)"/>(.*)</dd>(.*)'
        self.assertRegexpMatches(body, regexp, 'Virtual field not found')

    def test_image_filter(self):

        filters =['tag_image','tag_mini', 'tag_large', 'tag_thumb', 'tag_listing', 'tag_icon', 'tag_preview', 'tag_tile']
        for filter in filters:
            view = addView(self.portal, dict(
                id="myview",
                name="My View",
                item_fields=[],
                listing_fields=["lead_image:%s" % filter],
                restricted_to_types=[]
            ))
            fudgeRequest()
            body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
            regexp = '(.*)<dd class="listing-field field-lead_image-tag_image">(.*)<img src="http://nohost/plone/(.*)" alt="(.*)"/>(.*)</dd>(.*)'
            res = re.match(regexp,body, re.DOTALL | re.MULTILINE)
            image_url = str(res.group(3))
            image = self.portal.unrestrictedTraverse(image_url)
            self.assertIsNotNone(image, 'Image not found')


    def test_add_bad_custom_field(self):

        record = CustomFieldDefinition(dict(
            id="myfield",
            name="My Field",
            tal_statement="python: bad_variable"
        ))
        getRegistryFields().fields.append(record)

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=[":myfield"],
            restricted_to_types=[]
        ))
        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'The custom field expression has an error: python: bad_variable.', )


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
            restricted_to_types=[u'Folder', u'Collection' if plone_version >= "4.2.0" else "Topic"]
        ))

        body = self.portal.folder1.collection1.unrestrictedTraverse("@@"+view)()
        #self.assertRegexpMatches(body, '(?m)31/12/2000.*01/01/2001')
        # should be reverse date order
        self.assertLess(body.index("01/01/2001"), body.index("31/12/2000"))

    def test_change_viewid(self):
        # really want to test how to make tile views appearing after an upgrade but the usecase of renaming a view
        # should cover the same case of when the registrations get out of date

        view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["EffectiveDate:localshort"],
            restricted_to_types=[]
        ))

        menu = getUtility(IBrowserMenu, 'plone_displayviews')
        self.assertItemsSubset(['My View'], [m['title'] for m in menu.getMenuItems(self.portal.folder1, getRequest())])
        body = self.portal.folder1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'Jan 01, 2001', )

        # Now we change the view id
        old_view = view

        view = updateView(self.portal,
                         'myview',
                          dict(
                              id="updatedview",
                              name="Updated View",
                              item_fields=[],
                              listing_fields=["EffectiveDate:localshort"],
                              restricted_to_types=[]
                          ))

        self.assertItemsSubset(['Updated View'], [m['title'] for m in menu.getMenuItems(self.portal.folder1, getRequest())])
        self.assertNotIn(['My View'], [m['title'] for m in menu.getMenuItems(self.portal.folder1, getRequest())])
        try:
            self.portal.folder1.unrestrictedTraverse("@@"+old_view)()
        except AttributeError:
            pass
        body = self.portal.folder1.unrestrictedTraverse("@@"+view)()
        self.assertRegexpMatches(body, 'Jan 01, 2001', )



