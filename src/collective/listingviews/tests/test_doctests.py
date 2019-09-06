import unittest2 as unittest
import doctest

from plone.testing import layered

from collective.listingviews.testing import \
    COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING, COLLECTIVE_LISTINGVIEWS_FUNCTIONAL_TESTING, managerBrowser

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(
        doctest.DocFileSuite('listingviews.rst', optionflags=OPTIONFLAGS,
                             globs=dict(managerBrowser=managerBrowser)),
        layer=COLLECTIVE_LISTINGVIEWS_FUNCTIONAL_TESTING)]
    )
    return suite
