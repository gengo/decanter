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
        self.decanter.config.user = 'test_user'

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

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('decanter.vendor.daemon.Daemon.daemonize')
    @mock.patch('pwd.getpwuid')
    def test_daemonize(self, getpwuid, daemonize, isfile):
        m = mock.Mock()
        m.pw_name = 'test_user'
        getpwuid.return_value = m
        self.decanter.daemonize()

        daemonize.assert_called_once()

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('decanter.vendor.daemon.Daemon.daemonize')
    @mock.patch('pwd.getpwuid')
    @mock.patch('pwd.getpwnam')
    @mock.patch('grp.getgrnam')
    @mock.patch('os.chown')
    @mock.patch('os.setgid')
    @mock.patch('os.setuid')
    def test_daemonize_username_doesnt_match_config_user(self, setuid, setgid,  chown, getgrnam, getpwnam, getpwuid, daemonize, isfile):
        getpwuid_m = mock.Mock()
        getpwuid_m.pw_name = 'doesnt_match'

        m = mock.Mock()
        m.pw_uid = 1
        m.gr_gid = 1

        getpwuid.return_value = getpwuid_m
        getpwnam.return_value = m
        getgrnam.return_value = m

        self.decanter.daemonize()
        daemonize.assert_called_once()
        chown.assert_called_with('/var/run/decanter.pid', 1, 1)


if __name__ == '__main__':
    unittest.main()
