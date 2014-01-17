#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from mock import patch

from decanter.lib import i18n

class Tests(unittest.TestCase):
    def setUp(self):
        requestMock = mock.Mock()
        requestMock.environ = {}
        requestMock.headers = {}
        requestMock.url = 'http://gengo.com'
        self.request = patch.object(i18n, 'request', requestMock)
        self.request.start()

        config = mock.Mock()
        config.locale_dir = 'locale'
        config.supported_languages = ['en', 'ja']
        self.config = patch.object(i18n, 'Config', lambda: config)
        self.config.start()

    def tearDown(self):
        self.request.stop()
        self.config.stop()

    def test_get_translations(self):
        i18n.get_translations()

    def test_get_locale(self):
        i18n.get_locale()

    def test_gettext(self):
        i18n.gettext("test string")

    def test_ngettext(self):
        i18n.ngettext("singular", "plural", 0)

    def test_pgettext(self):
        i18n.pgettext("context", "test string")

    def test_npgettext(self):
        i18n.npgettext("context", "singular", "plural", 0)