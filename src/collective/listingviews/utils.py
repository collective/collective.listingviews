import inspect

from zope.component import getMultiAdapter, getUtility
#from settings import ListingSettings

from zope.interface import implements  # , alsoProvides
#from zope.schema import getFieldsInOrder
#from zope.schema.interfaces import RequiredMissing
from plone.registry.interfaces import IRecordsProxy, IRegistry
from plone.registry.recordsproxy import RecordsProxy, RecordsProxyCollection
from plone.registry import field
from plone.registry.record import Record
from zope import schema
import re
from collective.listingviews.interfaces import IListingControlPanel, IListingCustomFieldControlPanel
_marker = object()



# From http://code.activestate.com/recipes/440656/
import copy
import sys


# Public domain
class ListMixin(object):
    """
    Defines all list operations from a small subset of methods.

    Subclasses should define _get_element(i), _set_element(i, value),
    __len__(), _resize_region(start, end, new_size) and
    _constructor(iterable).  Define __iter__() for extra speed.

    The _get_element() and _set_element() methods are given indices with
    0 <= i < len(self).

    The _resize_region() method should resize the slice self[start:end]
    so that it has size new_size.  It is given indices such that
    start <= end, 0 <= start <= len(self) and 0 <= end <= len(self).
    The resulting elements in self[start:start+new_size] can be set to
    None or arbitrary Python values.

    The _constructor() method accepts an iterable and should return a
    new instance of the same class as self, populated with the elements
    of the given iterable.
    """
    def __cmp__(self, other):
        if '__iter__' not in dir(other):
            return -1
        return cmp(list(self), list(other))

    def __hash__(self):
        raise TypeError('list objects are unhashable')

    def __iter__(self):
        for i in xrange(len(self)):
            yield self._get_element(i)

    def _tuple_from_slice(self, i):
        """
        Get (start, end, step) tuple from slice object.
        """
        (start, end, step) = i.indices(len(self))
        # Replace (0, -1, 1) with (0, 0, 1) (misfeature in .indices()).
        if step == 1:
            if end < start:
                end = start
            step = None
        if i.step == None:
            step = None
        return (start, end, step)

    def _fix_index(self, i):
        if i < 0:
            i += len(self)
        if i < 0 or i >= len(self):
            raise IndexError('list index out of range')
        return i

    def __getitem__(self, i):
        if isinstance(i, slice):
            (start, end, step) = self._tuple_from_slice(i)
            if step == None:
                indices = xrange(start, end)
            else:
                indices = xrange(start, end, step)
            return self._constructor([self._get_element(i) for i in indices])
        else:
            return self._get_element(self._fix_index(i))

    def __setitem__(self, i, value):
        if isinstance(i, slice):
            (start, end, step) = self._tuple_from_slice(i)
            if step != None:
                # Extended slice
                indices = range(start, end, step)
                if len(value) != len(indices):
                    raise ValueError(('attempt to assign sequence of size %d' +
                                      ' to extended slice of size %d') %
                                     (len(value), len(indices)))
                for (j, assign_val) in enumerate(value):
                    self._set_element(indices[j], assign_val)
            else:
                # Normal slice
                if len(value) != (end - start):
                    self._resize_region(start, end, len(value))
                for (j, assign_val) in enumerate(value):
                    self._set_element(start + j, assign_val)
        else:
            # Single element
            self._set_element(self._fix_index(i), value)

    def __delitem__(self, i):
        if isinstance(i, slice):
            (start, end, step) = self._tuple_from_slice(i)
            if step != None:
                # Extended slice
                indices = range(start, end, step)
                # Sort indices descending
                if len(indices) > 0 and indices[0] < indices[-1]:
                    indices.reverse()
                for j in indices:
                    del self[j]
            else:
                # Normal slice
                self._resize_region(start, end, 0)
        else:
            # Single element
            i = self._fix_index(i)
            self._resize_region(i, i + 1, 0)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            ans = self._constructor(self)
            ans += other
            return ans
        return list(self) + other

    def __mul__(self, other):
        ans = self._constructor(self)
        ans *= other
        return ans

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            ans = other._constructor(self)
            ans += self
            return ans
        return other + list(self)

    def __rmul__(self, other):
        return self * other

    def __iadd__(self, other):
        self[len(self):len(self)] = other
        return self

    def __imul__(self, other):
        if other <= 0:
            self[:] = []
        elif other > 1:
            aux = list(self)
            for i in xrange(other - 1):
                self.extend(aux)
        return self

    def append(self, other):
        self[len(self):len(self)] = [other]

    def extend(self, other):
        self[len(self):len(self)] = other

    def count(self, other):
        ans = 0
        for item in self:
            if item == other:
                ans += 1
        return ans

    def reverse(self):
        for i in xrange(len(self) // 2):
            j = len(self) - 1 - i
            (self[i], self[j]) = (self[j], self[i])

    def index(self, x, i=0, j=None):
        if i != 0 or j is not None:
            (i, j, ignore) = self._tuple_from_slice(slice(i, j))
        if j is None:
            j = len(self)
        for k in xrange(i, j):
            if self._get_element(k) == x:
                return k
        raise ValueError('index(x): x not in list')

    def insert(self, i, x):
        self[i:i] = [x]

    def pop(self, i=None):
        if i == None:
            i = len(self) - 1
        ans = self[i]
        del self[i]
        return ans

    def remove(self, x):
        for i in xrange(len(self)):
            if self._get_element(i) == x:
                del self[i]
                return
        raise ValueError('remove(x): x not in list')

    # Define sort() as appropriate for the Python version.
    if sys.version_info[:3] < (2, 4, 0):
        def sort(self, cmpfunc=None):
            ans = list(self)
            ans.sort(cmpfunc)
            self[:] = ans
    else:
        def sort(self, cmpfunc=None, key=None, reverse=False):
            ans = list(self)
            if reverse == True:
                ans.sort(cmpfunc, key, reverse)
            elif key != None:
                ans.sort(cmpfunc, key)
            else:
                ans.sort(cmpfunc)
            self[:] = ans

    def __copy__(self):
        return self._constructor(self)

    def __deepcopy__(self, memo={}):
        ans = self._constructor([])
        memo[id(self)] = ans
        ans[:] = copy.deepcopy(tuple(self), memo)
        return ans

    # Tracking idea from R. Hettinger's deque class.  It's not
    # multithread safe, but does work with the builtin Python classes.
    def __str__(self, track=[]):
        if id(self) in track:
            return '...'
        track.append(id(self))
        ans = '%r' % (list(self),)
        track.remove(id(self))
        return ans

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self) + ')'


# Example usage:

class TestList(ListMixin):
    def __init__(self, L=[]):
        self.L = list(L)

    def _constructor(self, iterable):
        return TestList(iterable)

    def __len__(self):
        return len(self.L)

    def _get_element(self, i):
        assert 0 <= i < len(self)
        return self.L[i]

    def _set_element(self, i, x):
        assert 0 <= i < len(self)
        self.L[i] = x

    def _resize_region(self, start, end, new_size):
        assert 0 <= start <= len(self)
        assert 0 <= end <= len(self)
        assert start <= end
        self.L[start:end] = [None] * new_size


class ComplexRecordsProxy(RecordsProxy):
    """A proxy that maps an interface to a number of records, including collections of complex records
    """

    implements(IRecordsProxy)

    def __init__(self, registry, schema, omitted=(), prefix=None, key_names={}):
        # override to set key_names which changes how lists are stored
        super(ComplexRecordsProxy, self).__init__(registry, schema, omitted, prefix)
        self.__dict__['__key_names__'] = key_names

    def __getattr__(self, name):
        if name not in self.__schema__:
            raise AttributeError(name)

        _field = self.__schema__[name]
        if type(_field) in [schema.List, schema.Tuple]:
            prefix = self.__prefix__ + name
            factory = None
            key_name = self.__key_names__.get(name, None)
            return RecordsProxyList(self.__registry__, _field.value_type.schema, False, self.__omitted__, prefix, factory,
                                    key_name=key_name)
        elif type(_field) in [schema.Dict]:
            prefix = self.__prefix__ + name
            factory = None
            return RecordsProxyCollection(self.__registry__, _field.value_type.schema, False, self.__omitted__, prefix, factory)
        else:
            value = self.__registry__.get(self.__prefix__ + name, _marker)
            if value is _marker:
                value = self.__schema__[name].missing_value
            return value

    def __setattr__(self, name, value):
        if name in self.__schema__:
            full_name = self.__prefix__ + name
            _field = self.__schema__[name]
            if type(_field) in [schema.List, schema.Tuple]:
                proxy = self.__getattr__(name)
                proxy[:] = value
            elif type(_field) in [schema.Dict]:
                proxy = self.__getattr__(name)
                proxy[:] = value
            else:
                if full_name not in self.__registry__:
                    raise AttributeError(name)
                self.__registry__[full_name] = value
        else:
            self.__dict__[name] = value


class RecordsProxyList(ListMixin):
    """A proxy that represents a List of RecordsProxy objects.
        Two storage schemes are supported. A pure listing
        stored as prefix+"/i0001" where the number is the index.
        If your list has a field which can be used as a primary key
        you can pass they key_name in as an optional paramter. This will change
        the storage format where each entry is prefix+"/"+key_value which looks
        a lot nicer in the registry. Order is still
        kept in a special prefix+'.ordereddict_keys' entry.
    """

    def __init__(self, registry, schema, check=True, omitted=(), prefix=None, factory=None, key_name=None):
        self.map = RecordsProxyCollection(registry, schema, check, omitted, prefix, factory)
        self.key_name = key_name
        self.prefix = prefix
        self.registry = registry

    @property
    def keys(self):
        keys_key = self.prefix + '.ordereddict_keys'
        if self.registry.get(keys_key) is None:
            return []
        else:
            return self.registry.records[keys_key].value

    @keys.setter
    def keys(self, value):
        if self.key_name is None:
            raise Exception("No Supported")
        # will store as ordereddict with items stored using key_name's value and order kept in special keys list
        keys_key = self.prefix + '.ordereddict_keys'
        if self.registry.get(keys_key) is None:
            # Don't init until now to avoid a write on read error when no records yet. Assumes _resize_region
            # will call this first
            self.registry.records[keys_key] = Record(
                field.List(title=u"Keys of prefix",value_type=None), [])
        self.registry.records[keys_key].value = value


    def _get_element(self, i):
        return self.map[self.genKey(i)]

    def get(self, id, default=None):
        return self.map.get(id, default)

    def indexof(self, id):
        if self.key_name is not None:
            item = self.map.get(id)
            key = getattr(item, self.key_name)
            return self.keys.index(key)
        else:
            raise Exception('No key_name set')



    def _set_element(self, index, value):
        if self.key_name is not None:
            #First add it to the map to ensure it's a valid key
            try:
                key = getattr(value, self.key_name)
            except:
                key = value[self.key_name]
            assert key
            assert self.keys.count(key) == 0 or self.keys.index(key) == index
            self.map[key] = value

            # we have to remove the old value if it's being overwritten
            oldkey = self.keys[index]
            if key != oldkey and oldkey:
                del self.map[oldkey]
            self.keys[index] = key
            # Just to make sure we are init they record
            #self.keys = self.keys

        else:
            self.map[self.genKey(index)] = value

    def __len__(self):
        if self.key_name is None:
            return len(self.map)
        else:
            return len(self.keys)

    def _resize_region(self, start, end, new_size):
        if self.key_name is None:
            offset = new_size - (end - start)
            #move everything along one
            if offset > 0:
                for i in range(max(len(self.map) - 1, 0), start, -1):
                    self.map[self.genKey(i + offset)] = self.map[self.genKey(i)]
            else:
                for i in range(end, len(self.map), +1):
                    self.map[self.genKey(i + offset)] = self.map[self.genKey(i)]
                # remove any additional at the end
                for i in range(len(self.map) + offset, len(self.map)):
                    del self.map[self.genKey(i)]
        else:
            for i in range(start, end):
                del self.map[self.keys[i]]
            self.keys = self.keys[:start] + [ None for i in range(new_size)] + self.keys[end:]

    def genKey(self, index):
        if self.key_name is None:
            index_prefix = "i"
            return "%s%05d" % (index_prefix, index)
        else:
            if index < len(self.keys):
                return self.keys[index]
            # this could happen during registering menu items, not sure why
            raise StopIteration

def getViewName(view_id):
    return 'collective.listingviews.%s'%view_id

def getListingNameFromView(view_name):
    #TODO beter way then replace, could appear in the middle.
    return view_name.replace('collective.listingviews.', '')


def getRegistryViews():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IListingControlPanel, prefix='collective.listingviews',
                                key_names={'views':'id'})
    return proxy

def getRegistryFields():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IListingCustomFieldControlPanel,
                                   prefix='collective.listingviews.customfield',
                                   key_names={'fields': 'id'})
    return proxy
#
# class AdapterWhoKnowsItsName(object):
#
#     def __init__(self, *args, **kwargs):
#         super(AdapterWhoKnowsItsName, self).__init__(*args, **kwargs)
#         for frame, file, lineno, name, line, _ in inspect.stack():
#             # HACK
#             if 'zope/interface/adapter.py' in file and name == 'queryMultiAdapter':
#                 self.__adapter_name__ = inspect.getargvalues(frame).locals['name']
#

class NamedAdapterFactory(object):
    """ Useful when registering mutiple named views dynamically so view knows it's own name """

    def __init__(self, name, factory):
        self.name = name
        self.factory = factory
    def __call__(self, *args):
        args += (self.name,)
        return self.factory(*args)
