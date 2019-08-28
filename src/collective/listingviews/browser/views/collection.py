from zope.browser.interfaces import IBrowserView
from zope.component import adapts, getMultiAdapter, ComponentLookupError
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from basic import BasicListingInformationRetriever
from collective.listingviews.interfaces import IListingAdapter
from plone.memoize.instance import memoize
from Products.CMFPlone.PloneBatch import Batch
try:
    from plone.app.querystring import queryparser
except ImportError:
    pass

class BasicTopicListingInformationRetriever(BasicListingInformationRetriever):
    implements(IListingAdapter)

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        return self.context.queryCatalog(self.request,
                                         batch=True,
                                         b_size=self.listing_view_batch_size)

        #
        # query = self.context.buildQuery()
        # # preserver sort order and sort criteria
        #
        # if query is not None:
        #     if self.context.getSortCriterion():
        #         sort_crit = self.context.getSortCriterion()
        #         sort_crit_items = dict(sort_crit.getCriteriaItems())
        #         if sort_crit.getReversed():
        #             query['sort_order'] = 'descending'  # descending == reverse
        #         if 'sort_on' in sort_crit_items.keys():
        #             query['sort_on'] = sort_crit_items['sort_on']
        #
        #     should_limit = self.context.getLimitNumber()
        #     limit = self.context.getItemCount()
        #     if not limit:  # also make sure we have more than 0 items
        #         should_limit = False
        #     if should_limit:
        #         query['sort_limit'] = limit
        #     catalog = getToolByName(self.context, 'portal_catalog')
        #     items = catalog(query)
        #     if should_limit:
        #         items = items[:limit]
        # else:
        #     return []
        #
        # if self.listing_view_batch_size:
        #     items = Batch(items,
        #                   self.listing_view_batch_size,
        #                   int(self.request.get('b_start', 0)),
        #                   orphan=1)
        # return items


class ContentTypesCollectionListingInformationRetriever(
                            BasicTopicListingInformationRetriever):
    implements(IListingAdapter)

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """

        # Let's get the browser view for the collection
        # and get its' results
        # works for plone.app.contenttypes.interfaces.ICollection

        view = getMultiAdapter((self.context, self.request), name='listing_view')
        #view = view.__of__(self.context)

        results = view.results()
        return results

class AppCollectionListingInformationRetriever(
    BasicTopicListingInformationRetriever):
    implements(IListingAdapter)

    @property
    @memoize
    def retrieve_listing_items(self):

        # plone.app.collection
        # TODO: should probably use its code directly
        limit = self.context.limit
        query = queryparser.parseFormquery(self.context,
            self.context.getRawQuery())
        query['sort_limit'] = limit
        if self.context.sort_on:
            query['sort_on'] = self.context.sort_on
        if self.context.sort_reversed:
            query['sort_order'] = 'reverse'
        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(query)
        items = items[:limit]

        if self.listing_view_batch_size:
            items = Batch(items,
                self.listing_view_batch_size,
                int(self.request.get('b_start', 0)),
                orphan=1)
        return items
