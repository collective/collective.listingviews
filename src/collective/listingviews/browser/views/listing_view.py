from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from zope.interface import implements



class ListingView(BrowserView):
    index = ViewPageTemplateFile("templates/layout.pt")

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)


    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    @property
    def macros(self):
        return self.index.macros