from Products.CMFCore.utils import getToolByName
import json
from collective.plonetruegallery.settings import GallerySettings
from collective.plonetruegallery.settings import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotations


def install(context):
    if not context.readDataFile('collective.listingviews.txt'):
        return

    site = context.getSite()

    types = getToolByName(site, 'portal_types')
    if 'Collection' in types.objectIds():
        folder = types['Collection']
        view_methods = set(folder.view_methods)
        view_methods.add('listing_views')
        folder.view_methods = tuple(view_methods)


def export(context):
    import pdb
    pdb.set_trace()
    #pass


def uninstall(context):
    if not context.readDataFile('collective.listingviews.uninstall.txt'):
        return

    portal = context.getSite()

    #remove view
    types_to_remove = ('Folder', 'Topic', 'Collection')
    types = getToolByName(portal, 'portal_types')

    for _type in types_to_remove:
        if _type in types.objectIds():
            folder = types[_type]
            view_methods = list(folder.view_methods)
            view_methods.remove('listing_views')
            folder.view_methods = tuple(view_methods)
