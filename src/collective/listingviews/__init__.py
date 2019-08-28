# -*- coding: utf-8 -*-
from AccessControl import allow_class
from zope.i18nmessageid import MessageFactory
from pkg_resources import get_distribution


plone_version = get_distribution('Products.CMFPlone').version
LVMessageFactory = MessageFactory("collective.plonetruegallery")

# CatalogContentListingObject are used in the tal statements when creating
# custom listing columns so need to be accessible in RestrictedPython
try:
    from plone.app.contentlisting.catalog import CatalogContentListingObject
except ImportError:
    pass
else:
    allow_class(CatalogContentListingObject)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
