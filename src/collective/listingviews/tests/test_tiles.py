# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.namedfile import NamedImage
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from zope.component import createObject, getUtility
from zope.component import queryUtility

import random
import six
import transaction
from zope.schema.interfaces import IVocabularyFactory

from collective.listingviews.testing import COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING, TILES_INTEGRATION_TESTING


class ContentListingTileTests(TestCase):
    layer = TILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
        )

        self.unprivileged_browser = Browser(self.layer['app'])

        # setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # page_id = self.portal.invokeFactory(
        #     'Document', 'a-simple-page',
        #     title=u'A simple page', description=u'A description'
        # )
        # self.page = self.portal[page_id]
        # self.pageURL = self.portal[page_id].absolute_url()
        # transaction.commit()

    def test_contentlisting_tile_summary_view(self):
        """Any listing view we add to the control panel should be available as an option in a content listing tile
        """
        self.unprivileged_browser.open(
            self.portalURL +
            '/@@plone.app.standardtiles.contentlisting?' +
            'view_template=summary_view&' +
            'query.i:records=path&' +
            'query.o:records=plone.app.querystring.operation.string.relativePath&' +
            'query.v:records=..'
        )

        self.assertIn(u'item1', ' '.join(self.unprivileged_browser.contents.split()))

    def test_contentlisting_tile(self):

        self.unprivileged_browser.open(
            self.portalURL +
            '/@@plone.app.standardtiles.contentlisting?' +
            'view_template=collective.listingviews.myview&' +
            'query.i:records=path&' +
            'query.o:records=plone.app.querystring.operation.string.relativePath&' +
            'query.v:records=..'

        )

        html = ' '.join(self.unprivileged_browser.contents.split())
        self.assertIn(u'Dec 31, 2000', html)
        self.assertIn('<dt class="listing-field field-Title-tolink">Title (Link)</dt> '+
                      '<dd class="listing-field field-Title-tolink">'+
                      '<a href="http://nohost/plone/folder1/item1">item1</a></dd>', html)


    def test_contentlisting_tile_availbleviews(self):
        vocab = getUtility(IVocabularyFactory, name="Available Listing Views")(self.portal)
        self.assertIn("My View", [i.title for i in vocab] )
