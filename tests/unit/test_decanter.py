import mock
import unittest

from decanter import decanter
from decanter import lib

class DecanterTest(unittest.TestCase):
    @mock.patch('decanter.lib.config.Config.get_instance')
    def setUp(self, get_instance):
        app = mock.Mock()
        self.decanter = decanter.Decanter(app)
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
    @mock.patch('grp.getgrnam')
    @mock.patch.multiple('pwd', getpwuid=mock.DEFAULT, getpwnam=mock.DEFAULT)
    @mock.patch.multiple('os', chown=mock.DEFAULT, setgid=mock.DEFAULT, setuid=mock.DEFAULT)
    def test_daemonize_username_doesnt_match_config_user(self, getgrnam,  daemonize, isfile, getpwuid, getpwnam, chown, setgid, setuid):
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

    @mock.patch.object(decanter.pywsgi.WSGIServer, 'serve_forever')
    def test_run_calls_serve_forever(self, serve_forever):
        self.decanter.run()

        serve_forever.assert_called_once()

    @mock.patch.object(decanter.pywsgi, 'WSGIServer')
    def test_pywsgi_server_instantiated_with_right_args_with_config_test(self, WSGIServer):
        self.decanter.run()

        WSGIServer.assert_called_with((self.decanter.hostname, self.decanter.port),
                                       self.decanter.app, log=None)


    @mock.patch.object(decanter.pywsgi, 'WSGIServer')
    def test_pywsgi_server_instantiated_with_right_args_config_test_None(self, WSGIServer):
        self.decanter.config.test = None
        self.decanter.run()

        WSGIServer.assert_called_with((self.decanter.hostname, self.decanter.port),
                                       self.decanter.app, log='default')

    @mock.patch.object(decanter.Decanter, 'run')
    def test_runserver(self, run):
        self.decanter.runserver()

        run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
