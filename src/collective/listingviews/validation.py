import re
from collective.listingviews import LVMessageFactory as _
#from zope.interface import Invalid
from zope.schema import ValidationError
from zope.tales.tales import CompilerError
from Products.CMFCore.Expression import Expression


class InvalidId(ValidationError):
    __doc__ = _("Id must only containts alphanumeric or underscore, starting with alpha.")


class InvalidClass(ValidationError):
    __doc__ = _("""a name must begin with an underscore (_),
        a dash (-), or a letter(a-z), followed by any number of dashes,
        underscores, letters, or numbers.
        There is a catch: if the first character is a dash,
        the second character must2 be a letter or underscore,
        and the name must be at least 2 characters long.""")

class InvalidTAL(ValidationError):
    __doc__ = _("""TALES Compile Error""")

def validate_id(value):
    """
    Check that id only containts alphanumeric or underscore, starting with alpha.
    """
    #http://plone.org/documentation/manual/developer-manual/forms/using-zope.formlib/adding-validation
    if not re.match("^[A-Za-z][A-Za-z0-9_]*$", value):
        #raise Invalid(_(u"Id must only containts alphanumeric or underscore, starting with alpha."))
        raise InvalidId(value)
    return True


def validate_class(value):
    """
    Check that html or css class.
    """
    #http://www.w3.org/TR/CSS21/grammar.html#scanner
    #http://stackoverflow.com/questions/448981/what-characters-are-valid-in-css-class-names
    if not re.match("^-?[_a-zA-Z]+[_a-zA-Z0-9-]*$", value):
        #raise Invalid(_(u"Id must only containts alphanumeric or underscore, starting with alpha."))
        raise InvalidClass(value)
    return True

def validate_tal(value):
    """ Find compile bugs in tal """
    try:
        Expression(value)
    except CompilerError as e:
        raise InvalidTAL(value)
    return True
