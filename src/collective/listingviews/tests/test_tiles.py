# -*- coding: utf-8 -*-
import unittest

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from unittest import TestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from collective.listingviews.testing import TILES_INTEGRATION_TESTING, COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

from collective.listingviews import plone_version
PLONE5 = plone_version >= "5"


@unittest.skipIf(TILES_INTEGRATION_TESTING is None, "Tiles test not supported on Plone<5.0.x")
class ContentListingTileTests(TestCase):
    # Just to make the test runner happy
    layer = TILES_INTEGRATION_TESTING if TILES_INTEGRATION_TESTING is not None else COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

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
        self.assertIn('<dt class="listing-field field-Title-tolink">Title</dt> '+
                      '<dd class="listing-field field-Title-tolink">'+
                      '<a href="http://nohost/plone/folder1/item1">item1</a></dd>', html)


    def test_contentlisting_tile_availbleviews(self):
        vocab = getUtility(IVocabularyFactory, name="Available Listing Views")(self.portal)
        self.assertIn("My View", [i.title for i in vocab] )
