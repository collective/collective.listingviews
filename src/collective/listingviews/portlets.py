import re
import logging
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
#from plone.memoize.instance import memoize
from collective.listingviews import LVMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from Acquisition import aq_inner
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
#from collective.listingviews.settings import ListingSettings
from collective.listingviews.adapters import BasicAdapter
#from collective.listingviews.utils import getListingAdapter
#from zope.component import queryUtility
#from plone.registry.interfaces import IRegistry
#from collective.listingviews.interfaces import IListingDefinition
from collective.listingviews.adapters.base import BaseListingInformationRetriever
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic
from plone.app.collection.interfaces import ICollection
try:
    from plone.folder.interfaces import IFolder as IBaseFolder
except ImportError:
    from Products.Archetypes.interfaces import IBaseFolder


logger = logging.getLogger('collective.listingviews.listingbox')


class IListingPortlet(IPortletDataProvider):
    """A portlet which renders predefined static HTML.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        constraint=re.compile("[^\s]").match,
        required=True)

    listing_choice = schema.Choice(
        title=_(u"label_listing_choice", default=u"Listing views"),
        description=_(u"description_listing_choice",
            default=u"Select the custom listing views."),
        vocabulary="collective.listingviews.ListingViewVocabulary",
        required=True)

    root = schema.Choice(
            title=_(u"label_navigation_root_path", default=u"Root node"),
            description=_(u'help_navigation_root',
                          default=u"You may search for and choose a folder "
                                    "to act as the root of the navigation tree. "
                                    "Leave blank to use the Plone site root."),
            required=False,
            source=SearchableTextSourceBinder({},
                                              default_query='path:'))

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above "
            "without the standard header, border or footer."),
        required=False,
        default=False)


class ListingAssignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IListingPortlet)

    header = _(u"title_static_portlet", default=u"Static text portlet")
    listing_choice = u""
    root = u""
    omit_border = False

    def __init__(self, header=u"", listing_choice=u"", root=u"", omit_border=False):
        self.header = header
        self.listing_choice = listing_choice
        self.root = root
        self.omit_border = omit_border

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header

class ListingRenderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('listing-portlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()  # whether or not the current user is Anonymous
        self.portal_url = portal_state.portal_url()  # the URL of the portal object

        # a list of portal types considered "end user" types
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

        self.data_more_url = ""
        self.data_more_text = ""
        self.listing_information = []
        self._is_container = False
        if self.data.root:
            container = self._container()
            if container:
                if IATTopic.providedBy(container) or IBaseFolder.providedBy(container) or ICollection.providedBy(container):
                    self._is_container = True
                    adapter = BasicAdapter(container, self.request, self.data)
                    this_url = getattr(container, 'getPhysicalPath', None)
                    if this_url:
                        self.data_more_url = "/".join(this_url())
                    self.data_more_text = adapter.listing_portlet_more_text
                    self.listing_information = adapter.retrieve_items
                else:
                    # single content
                    adapter = BasicAdapter(container, self.request, self.data)
                    retriever = BaseListingInformationRetriever(container, adapter)
                    self.listing_information = retriever.assemble_listing_information(container)
        else:
            # current context don't have footer and more url
            adapter = BasicAdapter(context, self.request, self.data)
            retriever = BaseListingInformationRetriever(context, adapter)
            self.listing_information = retriever.assemble_listing_information(context)

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-listing-%s" % normalizer.normalize(header)

    def has_link(self):
        return bool(self.data_more_url)

    def has_footer(self):
        return bool(self.data.root)

    def more_url(self):
        return self.data_more_url

    def more_text(self):
        return self.data_more_text

    def is_container(self):
        return self._is_container

    def _container(self):
        try:
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            portal = portal_state.portal()
            path = self.data.root
            if path and path.startswith('/'):
                # https://github.com/plone/plone.portlet.static
                path = path[1:]

            return portal.restrictedTraverse(path, default=False)
        except:
            return False

    def portlet_items(self):
        """Main function that do everything.
        """
        return self.listing_information


class ListingAddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IListingPortlet)
    label = _(u"title_add_static_portlet", default=u"Add static text portlet")
    description = _(u"description_static_portlet",
        default=u"A portlet which can display static HTML text.")

    def create(self, data):
        return ListingAssignment(
            header=data.get("header", u""),
            listing_choice=data.get("listing_choice", u""),
            root=data.get("root", u""),
            omit_border=data.get("omit_border", False))


class ListingEditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IListingPortlet)
    label = _(u"title_edit_static_portlet", default=u"Edit static text portlet")
    description = _(u"description_static_portlet",
        default=u"A portlet which can display static HTML text.")
