from zope.component.hooks import getSite

from collective.listingviews.browser.views.controlpanel import syncViews
from collective.listingviews.utils import getRegistryViews, getRegistryFields


def run_before(context):
    pass

def run_after(contenxt):
    pass

def run_before_uninstall(context):
    fields = getRegistryFields().fields
    for f in fields:
        fields.pop()
    assert len(getRegistryFields().fields) == 0

    views = getRegistryViews().views
    for i in views:
        views.pop()
    assert len(getRegistryViews().views) == 0
    syncViews(getSite())


def run_after_uninstall(context):
    pass