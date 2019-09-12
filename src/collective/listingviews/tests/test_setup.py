# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest

from zope.browser.interfaces import IBrowserView
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility, getGlobalSiteManager, ComponentLookupError, getSiteManager
from zope.publisher.interfaces.browser import IDefaultBrowserLayer, IBrowserRequest
from zope.schema.interfaces import IVocabularyFactory

from collective.listingviews.browser.views.controlpanel import addView
from collective.listingviews.testing import COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING
from collective.listingviews.utils import getRegistryViews, getRegistryFields

no_get_installer = False

try:
    from Products.CMFPlone.utils import get_installer
except Exception:
    # Quick shim for 5.1 api change

    class get_installer(object):
        def __init__(self, portal, request):
            self.installer = getToolByName(portal, 'portal_quickinstaller')

        def is_product_installed(self, name):
            return self.installer.isProductInstalled(name)

        def uninstall_product(self, name):
            return self.installer.uninstallProducts([name])


class TestSetup(unittest.TestCase):
    """Test that collective.collectionfilter is properly installed."""

    layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        self.view = addView(self.portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["getObjSize:"],
            restricted_to_types=['Document']
        ))

    def test_product_installed(self):
        """Test if collective.collectionfilter is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'collective.listingviews'))

    def test_browserlayer(self):
        """Test that ICollectionFilterBrowserLayer is registered."""
        from collective.listingviews.interfaces import (
            IListingViewsBrowserLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IListingViewsBrowserLayer,
            utils.registered_layers())


    def test_uninstall_fti(self):
        self.installer.uninstall_product('collective.listingviews')

        portal_types = getToolByName(self.portal, "portal_types")
        ftis =[(name,fti) for fti in portal_types.listTypeInfo() for name in getattr(fti, 'view_methods', []) if
                     name.startswith('collective.listingviews.')]
        self.assertListEqual([], ftis)


    def test_uninstall_views(self):
        self.installer.uninstall_product('collective.listingviews')


        lsm = getSiteManager(self.portal)
        adapters = [(n, f) for n, f in lsm.adapters.lookupAll((IContentish, IBrowserRequest), IBrowserView) if
                         n.startswith('collective.listingviews.')]
        self.assertListEqual([], adapters)

        try:
            view = self.portal.folder1.collection1.unrestrictedTraverse("@@"+self.view)
        except AttributeError:
            pass
        else:
            self.assertTrue(False, 'Listing view still callable %s' % view)

        # TODO: ensure portlets are gone

    def test_uninstall_displaymenu(self):
        self.installer.uninstall_product('collective.listingviews')

        menu = getUtility(IBrowserMenu, 'plone_displayviews')
        gsm = getGlobalSiteManager()
        adapters = [(n, f) for n, f in
                    gsm.adapters.lookupAll((IContentish, IDefaultBrowserLayer), menu.getMenuItemType()) if
                    n.startswith('collective.listingviews.')]
        self.assertListEqual([], adapters)


    def test_uninstall_registry(self):
        self.installer.uninstall_product('collective.listingviews')

        views = [(view.id, view) for view in getRegistryViews().views]
        self.assertListEqual([], views)

        fields = [(view.id, view) for view in getRegistryFields().fields]
        self.assertListEqual([], fields)



def getRoles(portal, user_id):
    userFolder = portal['acl_users']
    return userFolder.getUserById(user_id).getRoles()


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        roles_before = getRoles(self.portal, TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('collective.listingviews')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.collectionfilter is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.listingviews'))
    #
    # def test_browserlayer_removed(self):
    #     """Test that ICollectionFilterBrowserLayer is removed."""
    #     from collective.collectionfilter.interfaces import \
    #         ICollectionFilterBrowserLayer
    #     from plone.browserlayer import utils
    #     self.assertNotIn(
    #         ICollectionFilterBrowserLayer,
    #         utils.registered_layers())
