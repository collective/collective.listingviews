from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from collective.listingviews.interfaces import IListingSettings


class LVVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
    This prevents any issues if a gallery or display
    type is removed and the user had it selected.
    """

    def __init__(self, terms, *interfaces, **config):
        try:
            super(LVVocabulary, self).__init__(terms, *interfaces)
        except:
            import pdb
            pdb.set_trace()
            raise
        if 'default' in config:
            self.default = config['default']
        else:
            self.default = None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)

#Temp object
list_views = [{'name':'view1', 'description':'listing view1'},
    {'name':'view2', 'description':'listing view2'},
    {'name':'view3', 'description':'listing view3'},
    {'name':'view4', 'description':'listing view4'},
    {'name':'view5', 'description':'listing view5'},
    {'name':'view6', 'description':'listing view6'},
    {'name':'view7', 'description':'listing view7'},
    {'name':'view8', 'description':'listing view8'}]
GLOBAL_FIELDS = {
    'view1': ['Title'],
    'view2': ['Title', 'Description'],
    'view3': ['Title', 'Path'],
    'view4': ['Title', 'modified'],
    'view5': ['Title', 'Path', 'modified'],
    'view6': ['Title', 'Description', 'modified'],
    'view7': ['Title', 'Description', 'Path'],
    'view8': ['Title', 'Description', 'Path', 'modified']
    }


def ListingViewVocabulary(context):
    items = []
    for t in list_views:
        items.append(SimpleTerm(t['name'], t['name'], t['description']))

    return LVVocabulary(items,
                default=IListingSettings['listing_choice'].default)
