from zope.component.hooks import getSite

from collective.listingviews.browser.views.controlpanel import syncViews
from collective.listingviews.utils import getRegistryViews, getRegistryFields

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'collective.listingviews:uninstall',
        ]


def run_before(context):
    pass

def run_after(context):
    if context.readDataFile('collectivelistingviews_install.txt') is None:
        return
    pass

def uninstall(context):
    if context.readDataFile('collectivelistingviews_uninstall.txt') is None:
        return

    fields = getRegistryFields().fields
    for f in fields:
        fields.pop()
    assert len(getRegistryFields().fields) == 0

    views = getRegistryViews().views
    for i in views:
        views.pop()
    assert len(getRegistryViews().views) == 0
    syncViews(context.getSite())

    # TODO: might need to do more to get rid of old registrations
    #  see - https://github.com/plone/plone.multilingualbehavior/blob/master/plone/multilingualbehavior/setuphandlers.py


def run_after_uninstall(context):
    pass