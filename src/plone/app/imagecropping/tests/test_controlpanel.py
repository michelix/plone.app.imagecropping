# -*- coding: utf-8 -*-

from plone.app.imagecropping.browser.settings import ISettings
from plone.app.imagecropping.testing import PLONE_APP_IMAGECROPPING_INTEGRATION
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest2 as unittest


class ControlPanelTestCase(unittest.TestCase):

    layer = PLONE_APP_IMAGECROPPING_INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']
        self.setup_tool = self.portal['portal_setup']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_controlpanel_has_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='imagecropping-settings')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@imagecropping-settings')

    def test_controlpanel_installed(self):
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertIn('imagecropping.settings', actions,
                      'control panel was not installed')

    @unittest.expectedFailure
    def test_controlpanel_removed_on_uninstall(self):
        # run uninstall profile instead of uninstall in quickinstaller.
        # QI does not pay attention to uninstall profiles
        # see https://dev.plone.org/ticket/11328
        # XXX: Configlet removal doesn't seem to work in GenericSetup :(
        self.setup_tool.runAllImportStepsFromProfile(
            'profile-plone.app.imagecropping:uninstall')
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertNotIn('imagecropping.settings', actions,
                         'control panel was not removed')


class RegistryTestCase(unittest.TestCase):

    layer = PLONE_APP_IMAGECROPPING_INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_tool = self.portal['portal_setup']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(ISettings)

    def test_available_sections_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'large_size'))
        self.assertEqual(self.settings.large_size, u"768:768")

    def test_default_section_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'min_size'))
        self.assertEqual(self.settings.min_size, u"50:50")

    def test_records_removed_on_uninstall(self):
        # run uninstall profile instead of uninstall in quickinstaller.
        # QI does not pay attention to uninstall profiles
        # see https://dev.plone.org/ticket/11328
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.setup_tool.runAllImportStepsFromProfile(
            'profile-plone.app.imagecropping:uninstall')

        BASE_REGISTRY = 'plone.app.imagecropping.browser.settings.ISettings.%s'
        records = (
            BASE_REGISTRY % 'large_size',
            BASE_REGISTRY % 'min_size',
        )

        for r in records:
            self.assertNotIn(r, self.registry)
