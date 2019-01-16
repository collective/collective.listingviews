import unittest2 as unittest
import doctest
from collective.listingviews.testing import\
    COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING

from collective.listingviews import plone_version
plone5 = plone_version >= "5"
OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE


def test_suite():
    suite = unittest.TestSuite()
#    seltest = doctest.DocFileSuite('selenium.rst', optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
#    seltest.level = 2
    layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING
    suite.addTests([
        doctest.DocFileSuite('tests/listingviews.rst', optionflags=OPTIONFLAGS, globs=dict(layer=layer, plone5=plone5)),
        doctest.DocFileSuite('tests/listingviews_sortable_collections.rst', optionflags=OPTIONFLAGS, globs=dict(layer=layer)),
    ])
    suite.layer = COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING
    return suite