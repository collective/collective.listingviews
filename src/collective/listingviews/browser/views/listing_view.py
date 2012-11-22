from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements



class ListingView(BrowserView):
    index = ViewPageTemplateFile("templates/layout.pt")

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        view_name = request.getURL().split('/')[-1]
        listing_view_name = view_name.rsplit('.', 1)[-1]
        # our template will adapt the context and that view will use this value
        request.set('view_name',listing_view_name)


    def render(self):
        #print "*** ListingView render %s" % self.settings.listing_choice
        return self.index()

    def __call__(self):
        #print "*** ListingView call %s" % self.settings.listing_choice
        return self.render()
