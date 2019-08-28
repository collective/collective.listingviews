from zope.interface import Interface, Attribute
from zope import schema
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter, FactoryAdapter
from collective.listingviews import LVMessageFactory as _
from validation import validate_id, validate_class, validate_tal
try:
    from plone.autoform import directives as form
except:
    from plone.directives import form
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite


class ICustomFieldDefinition(Interface):
    id = schema.ASCIILine(title=(u"Id"),
                          required=True,
                          description=_(u"It must contains only alphanumeric or underscore, starting with alpha. Will be used as css class"),
                          constraint=validate_id)

    name = schema.ASCIILine(title=_(u"Title"),
                            description=_(u"Name as it will appear in html of view"),
                            required=False)

    tal_statement = schema.ASCIILine(title=_(u"TAL expression"),
                                     required=True,
                                     description=_(u'variables available include "item":catalog brain, "object": context object, "folder": parent of object if object is not a folder. e.g. "python:item.getObject().getBody()"'),
                                     constraint=validate_tal)

    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"),
                                 required=False,
                                 constraint=validate_class,
                                 default=""
                                 )


class IListingDefinition(Interface):
    id = schema.ASCIILine(title=_(u"Id"),
                          required=True,
                          description=_(
                              u"Unique id of your listing (will appear as css class). It must contains only alphanumeric or underscore, starting with alpha"),
                          constraint=validate_id)

    name = schema.ASCIILine(title=_(u"Title"),
                            required=False,
                            description=_(u"Name as it will appear in the display menu to editors"))

    # http://plone.org/products/dexterity/documentation/manual/developer-manual/advanced/vocabularies/
#    form.widget(item_fields=ChosenMultiFieldWidget)
    item_fields = schema.List(title=_(u"Item Fields"),
                              description=_(
                                  u"Display the following fields at of current content item. Sort to change order."),
                              required=False,
                              default=[],
                              value_type=schema.Choice(
                                              vocabulary="collective.listingviews.MetadataVocabulary",
                              )
    )

#    form.widget(listing_fields=ChosenMultiFieldWidget)
    listing_fields = schema.List(title=_(u"Listing Fields"),
                                 description=_(
                                     u"Folders/Collections and other listable items will list contents displaying these fields for each"),
                                 required=False,
                                 default=[],
                                 value_type=schema.Choice(
                                                 vocabulary="collective.listingviews.MetadataVocabulary",
                                 )
    )

    #    form.widget(restricted_to_types=AutocompleteMultiSelectionFieldWidget)
    restricted_to_types = schema.List(title=_(u"Enabled on Types"),
                                      description=_(u"Show in display menu or make portlet visible only for these types"),
                                      required=True,
                                      value_type=schema.Choice(
                                          vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"
                                      ),
    )

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size"),
        description=_(u"description_batch_size",
                      default=u"The amount of items shown in one page. "
                              u"Enter zero if you want to disable view batching."
        ),
        default=10,
        required=True)

    portlet_more_text = schema.ASCIILine(title=_(u"Portlet Read More Text"), required=False)

    css_class = schema.ASCIILine(title=_(u"Additional CSS classes"),
                                 required=False,
                                 constraint=validate_class)



#class IListingSettings(Interface):
#    listing_choice = schema.Choice(
#        title=_(u"label_listing_choice", default=u"Listing views"),
#        description=_(u"description_listing_choice",
#            default=u"Select the custom listing views."),
#        vocabulary="collective.listingviews.ListingViewVocabulary",
#        default="view1")


class IListingControlSettings(Interface):
    pass


class IListingControlPanel(Interface):
    views = schema.List(
        title=_(u'Custom listing views'),
        description=(
        u"Create and manage your custom listing views which can be used in collections, folders, portlets and tiles"),
        value_type=schema.Object(IListingDefinition,
                                 title=_(u"Listing View")),
        required=False,
        default=[],
        missing_value=[],
    )


class IListingCustomFieldControlPanel(Interface):
    fields = schema.Tuple(
        title=_(u'Names of custom listing fields'),
        description=_(
        u"Create new fields to insert into your Listing Views based on existing fields of data from your content"),
        value_type=schema.Object(ICustomFieldDefinition,
                                 title=_(u"Custom Field Definition")),
        required=False,
        default=(),
        missing_value=(),
    )


class ListingDefinition(object):
    implements(IListingDefinition)

    def __init__(self, data={}):
        for key,value in data.items():
            setattr(self, key, value)


class ListingDefinitionFactory(FactoryAdapter):
    factory = ListingDefinition


class CustomFieldDefinition(object):
    implements(ICustomFieldDefinition)

    def __init__(self, data={}):
        for key,value in data.items():
            setattr(self, key, value)


class CustomFieldDefinitionFactory(FactoryAdapter):
    factory = CustomFieldDefinition


class IListingAdapter(Interface):
    def retrieve_context_item(self):
        """
        This method retrieves all the item fields
        """

    def retrieve_listing_items(self):
        """
        This method retrieves all the listing fields
        """

    def number_of_items(self):
        """
        Total items of the current list
        """

    def listing_style_class(self):
        """
        Listing view css class
        """

    def listing_view_batch_size(self):
        """
        Batch size
        """

    def set_listing_view(self, view_name):
        """
        Set id of the view to one of the available views stored in the registry.
        """

    def is_container(self):
        """
        Return true if current object is a container, such as folder, or collection
        """
