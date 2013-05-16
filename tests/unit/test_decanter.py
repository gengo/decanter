import mock
import unittest

from decanter.decanter import Decanter
from decanter import lib
from decanter.vendor.daemon import Daemon

class DecanterTest(unittest.TestCase):
    @mock.patch('decanter.lib.config.Config.get_instance')
    def setUp(self, get_instance):
        app = mock.Mock()
        self.decanter = Decanter(app)

    @mock.patch('bottle.install')
    def test_install(self, bottle_install):
        json_plugin = mock.Mock()
        xml_plugin = mock.Mock()
        lib.plugin = mock.Mock()
        lib.plugin.JsonPlugin = json_plugin
        lib.plugin.XmlPlugin = xml_plugin

        self.decanter.install(['json', 'xml'])
        bottle_install.assert_any_call(json_plugin())
        bottle_install.assert_any_call(xml_plugin())


if __name__ == '__main__':
    unittest.main()
