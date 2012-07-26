from zope.interface import Interface


class ILVUtility(Interface):
    """
    utility methods for collective.listingviews
    """

    def enabled():
        """
        Lets you know if the listing view is enabled
        """
