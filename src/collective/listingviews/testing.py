from plone.app.testing import PLONE_FIXTURE, PLONE_FUNCTIONAL_TESTING, PLONE_INTEGRATION_TESTING
from plone.app.testing import PloneSandboxLayer, FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from plone.uuid.interfaces import IUUID
from zope.configuration import xmlconfig
from plone.testing.z2 import Browser
from zope.testbrowser.browser import controlFactory, ItemControl
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, setRoles, login
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from Products.CMFCore.utils import getToolByName
from lxml import etree


class CollectiveListingviews(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        try:
            import plone.app.contenttypes
            import plone.app.event.dx
            self.loadZCML(package=plone.app.contenttypes)
            self.loadZCML(package=plone.app.event.dx)
        except ImportError:
            # plone 4
            pass

        # Load ZCML for this package
        import collective.listingviews
        xmlconfig.file('configure.zcml',
                       collective.listingviews,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        try:
            applyProfile(portal, 'plone.app.contenttypes:default')
        except KeyError:
            # plone 4
            pass

        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        applyProfile(portal, 'collective.listingviews:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        workflowTool = getToolByName(portal, 'portal_workflow')

        portal.invokeFactory('Folder', 'folder1', title=u"folder1")
        portal.folder1.invokeFactory('Document', 'item1', title=u"item1")
        workflowTool.doActionFor(portal.folder1.item1, 'publish')
        portal.folder1.item1.setEffectiveDate('1/1/2001')
        portal.folder1.item1.reindexObject()

        portal.folder1.invokeFactory('Document', 'item2', title=u"item2")
        workflowTool.doActionFor(portal.folder1.item2, 'publish')
        portal.folder1.item2.setEffectiveDate('12/31/2000')
        portal.folder1.item2.reindexObject()

        try:
            portal.folder1.invokeFactory('Collection', 'collection1', title=u"collection1")
        except ValueError:
            portal.folder1.invokeFactory('Topic', 'collection1', title=u"collection1")
            topic = portal.folder1.collection1
            path_crit = topic.addCriterion('path', 'ATRelativePathCriterion')
            path_crit.setRelativePath('..')   # should give the parent==folderA1
            topic.setSortCriterion('effective', True) #
        else:
            collection = portal.folder1.collection1
            query = [{
                        'i': 'path',
                        'o': 'plone.app.querystring.operation.string.relativePath',
                        'v': '..',
                    }]
                    # set the query and publish the collection
            collection.setQuery(query)
            collection.sort_on = u'effective'
            collection.sort_reversed = True

        portal.folder1.collection1.reindexObject()

class CollectiveListingviewsTiles(CollectiveListingviews):

    def setUpZope(self, app, configurationContext):
        super(CollectiveListingviewsTiles, self).setUpZope(app, configurationContext)
        # load ZCML
        # import plone.app.dexterity
        # xmlconfig.file('configure.zcml', plone.app.dexterity,
        #                context=configurationContext)
        #
        # import plone.app.widgets
        # xmlconfig.file('configure.zcml', plone.app.widgets,
        #                context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('testing.zcml', plone.app.standardtiles,
                       context=configurationContext)
        #
        # import plone.app.contenttypes
        # xmlconfig.file('configure.zcml', plone.app.contenttypes,
        #                context=configurationContext)

        try:
            import plone.app.drafts
            xmlconfig.file('configure.zcml', plone.app.drafts,
                           context=configurationContext)
        except ImportError:
            pass

    def setUpPloneSite(self, portal):
        super(CollectiveListingviewsTiles, self).setUpPloneSite(portal)
        # install into the Plone site
        # applyProfile(portal, 'plone.app.dexterity:default')
        # applyProfile(portal, 'plone.app.widgets:default')
        applyProfile(portal, 'plone.app.standardtiles:default')
        # applyProfile(portal, 'plone.app.contenttypes:default')

        try:
            # testing support when plone.app.drafts is installed in the env.
            # it needs to also be configured for these tests...
            import plone.app.drafts  # noqa
            applyProfile(portal, 'plone.app.drafts:default')
        except ImportError:
            pass


        # Add a simple listing view

        from collective.listingviews.browser.views.controlpanel import addView

        addView(portal, dict(
            id="myview",
            name="My View",
            item_fields=[],
            listing_fields=["Title:", "Title:tolink", "EffectiveDate:localshort"],
            restricted_to_types=[]
        ))



        #
        # # ensure plone.app.theming disabled
        # from plone.registry.interfaces import IRegistry
        # from zope.component import getUtility
        # registry = getUtility(IRegistry)
        # key = 'plone.app.theming.interfaces.IThemeSettings.enabled'
        # if key in registry:
        #     registry[key] = False
        #
        # # creates some users
        # acl_users = getToolByName(portal, 'acl_users')
        # acl_users.userFolderAddUser(
        #     NORMAL_USER_NAME,
        #     NORMAL_USER_PASSWORD,
        #     ['Member'],
        #     [],
        # )
        # acl_users.userFolderAddUser(
        #     EDITOR_USER_NAME,
        #     EDITOR_USER_PASSWORD,
        #     ['Editor'],
        #     [],
        # )
        # acl_users.userFolderAddUser(
        #     MANAGER_USER_NAME,
        #     MANAGER_USER_PASSWORD,
        #     ['Manager'],
        #     [],
        # )
        #
        # # register portlet manager and portlet manager renderer
        # sm = getSiteManager(portal)
        # sm.registerUtility(component=MockPortletManager(),
        #                    provided=IMockPortletManager,
        #                    name='mock.portletmanager')
        # provideAdapter(MockPortletManagerRenderer)
        #
        # from plone.app.standardtiles import embed
        # embed.requests.get = RequestsGetMock


class BrowserIntegrationTesting(IntegrationTesting):

    def setUpEnvironment(self, portal):
        super(BrowserIntegrationTesting, self).setUpEnvironment(portal)
        #portal = self['portal']

        browser = Browser(portal)
        browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        self['manager'] = browser

        browser.handleErrors = False
        portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

        browser.open(portal.absolute_url())

    def getFormFromControl(self, control):
        browser = control.browser
        index = 0
        while True:
            try:
                form = browser.getForm(index=index)
            except:
                return None
            if hasattr(control,'mech_form') and form.mech_form == control.mech_form:
                return form
            elif hasattr(control, '_form') and form._form == control._form:
                return form
            else:
                index += 1
                continue

    def getControls(self, form):
        if getattr(form, 'mech_control', None) is not None or getattr(form, 'mech_item', None) is not None:
            return getattr(form, 'controls', [])
        else:
            #assume its a form
            return [controlFactory(c, form.mech_form, form.browser) for c in form.mech_form.controls]

    def isSameControl(self, subcontrol, control):
        try:
            if subcontrol.mech_control == control.mech_control:
                return True
        except:
            pass
        try:
            if subcontrol.mech_item == control.mech_item:
                return True
        except:
            pass
        return False



    def getControlParents(self, control, parents=[]):
        if not parents:
            parents = [self.getFormFromControl(control)]
        parent = parents[-1]
        for subcontrol in self.getControls(parent):
            if self.isSameControl(subcontrol, control):
                return parents
            new_parents = self.getControlParents(control, parents+[subcontrol])
            if new_parents:
                return new_parents
        return None


    def setInAndOut(self, browser, labels, index=None):
        main_control = browser.getControl(labels[0], index=index).control
        #parents = self.getControlParents(main_control)
        #form = self.getFormFromControl(main_control)
        #import pdb; pdb.set_trace()

        name = main_control.name.rstrip('.to').rstrip('.from')
        def get_label(control):
            if hasattr(control, 'labels'):
                return control.labels[0]
            else:
                return control.mech_item._labels[0]._text

        options = dict([(get_label(i), i.optionValue) for i in main_control.controls])

        def insert_input(control, name, value, index):
            # HACK to insert new text input into page dynamically
            if hasattr(control, 'mech_form'):
                control.mech_form.new_control('text', name, attrs=dict(value=value), index=index)
            else:
                #bshtml = list(control._elem.parents)[-1]
                #item = bshtml.new_tag("input", attrs=dict(type="text", name=name, value=label))
                #control._elem.insert_before(item) #before so they go in the right order
                form = control._form
                import webtest
                field = webtest.forms.Field(form, "input", name, index, value=value)
                form.fields.setdefault(name, []).append(field)
                form.field_order.append((name, field))

        index = 0
        for label in labels:
            value = None
            if label not in options:
                raise Exception("No item found with label '%s' in %s" % (label, options.keys()))
            insert_input(main_control, '%s:list'%name, options[label], index)
            index += 1

        #import pdb;
        #pdb.set_trace()

    def setRelatedItem(self, browser, label, path):
        name = etree.HTML(browser.contents).xpath("//label[.//text()[contains(.,'%s')]]/@for" % label)[0]
        name = name.replace("-",".")
        try:
            control = browser.getControl(name=name)
        except:
            # Older style widget
            control = browser.getControl(name=name+".query.query")
            form = self.getFormFromControl(control)
            form.mech_form.new_control('text', name, {'value': "/"+path})
        else:
            item = self['portal'].restrictedTraverse(path)
            control.value = IUUID(item)

    def errorlog(self):
        from Products.CMFCore.utils import getToolByName
        portal = self['portal']
        errorLog = getToolByName(portal, 'error_log')
        print errorLog.getLogEntries()[-1]['tb_text']



COLLECTIVE_LISTINGVIEWS_FIXTURE = CollectiveListingviews()
COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING = \
    BrowserIntegrationTesting(bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE, ),
                            name="CollectiveListingviews:Integration")

# FIXTURE = CollectiveListingviews()
# INTEGRATION_TESTING = IntegrationTesting(
#     bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
#     name='example.conference:Integration',
#     )
# FUNCTIONAL_TESTING = FunctionalTesting(
#     bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
#     name='example.conference:Functional',
#     )

try:
    import plone.app.standardtiles

    TILES_FIXTURE = CollectiveListingviewsTiles()
    TILES_INTEGRATION_TESTING = \
        BrowserIntegrationTesting(bases=(TILES_FIXTURE,),
                                  name="CollectiveListingviewsTiles:Integration")
except ImportError:
    TILES_INTEGRATION_TESTING = None
