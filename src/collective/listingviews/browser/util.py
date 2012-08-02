from zope.interface import implements
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from interfaces import ILVUtility


class LVUtility(BrowserView):
    """Information about the state of the portal
    """
    implements(ILVUtility)

    @memoize
    def enabled(self):
        utils = getToolByName(self.context, 'plone_utils')
        try:
            return utils.browserDefault(self.context)[1][0] == "listing_views"
        except:
            return False
