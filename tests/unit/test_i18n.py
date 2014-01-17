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
        requestMock.headers = {'Accept-Language': 'ja,zh;q=0.8,en-US;q=0.6,en;q=0.4,af;q=0.2'}
        requestMock.url = 'http://gengo.com'
        self.request = patch.object(i18n, 'request', requestMock)
        self.request.start()

        config = mock.Mock()
        config.locale_dir = 'locale'
        config.lang_code = 'en'
        config.supported_languages = ['en', 'ja']
        self.configMock = config
        self.config = patch.object(i18n, 'Config', lambda: config)
        self.config.start()

        self.translationMock = mock.Mock()
        self.translationLoadMock = mock.Mock()
        self.translationLoadMock.ungettext.return_value = 'ungettext'
        self.translationLoadMock.unpgettext.return_value = 'unpgettext'
        self.translationMock.load = mock.Mock(return_value=self.translationLoadMock)
        self.translation = patch.object(i18n.support, 'Translations', self.translationMock)
        self.translation.start()

    def tearDown(self):
        self.request.stop()
        self.config.stop()
        self.translation.stop()

    def test_get_translations(self):
        t = i18n.get_translations()
        self.assertEqual(t, self.translationMock.load.return_value)

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

    def test_extra_client_expected_langs(self):
        self.assertEqual(i18n.extra_client_expected_langs(), [('ja', 1.0), ('zh', 0.8), ('en-US', 0.6), ('en', 0.4), ('af', 0.2)])

    def test_get_language_list(self):
        self.assertEqual(i18n.get_language_list(), ['ja', 'zh', 'en_US', 'en_us', 'en', 'af', 'en'])

    def test_get_ui_lc_returns_none(self):
        self.assertEqual(i18n.get_ui_lc(), None)
