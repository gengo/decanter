#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pwd
import grp
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
import bottle
from datetime import date
from vendor.daemon import Daemon
from lib.middleware import Dispatcher
from lib.middleware import StripPath
from lib.config import Config
import lib.plugin
from lib.logger import Log


class Decanter(Daemon):
    def __init__(self, app, hostname='localhost', port=9000, pidfile = '/var/run/decanter.pid'):
        self.app = app
        self.hostname = hostname
        self.port = int(port)
        self.pidfile = pidfile
        self.config = Config.get_instance()

        # remove all default bottle plugins
        bottle.uninstall(True)
        bottle.DEBUG = self.config.debug
        # install plugins
        self.install(plugins=self.config.plugins)
        if self.config.debug:
            stdout = os.popen('tty').read().strip()
            stderr = os.popen('tty').read().strip()

        super(Decanter, self).__init__(pidfile, stdout=stdout, stderr=stderr)

    def install(self, plugins=[]):
        for plugin in plugins:
            name = ''.join([plugin.lower().capitalize(), 'Plugin'])
            cls = getattr(lib.plugin, name)
            bottle.install(cls())

    def daemonize(self):
        haspid = os.path.isfile(self.pidfile)
        super(Decanter, self).daemonize()

        username = pwd.getpwuid(os.getuid()).pw_name
        if username != self.config.user:
            uid = pwd.getpwnam(self.config.user).pw_uid
            gid = grp.getgrnam(self.config.group).gr_gid
            os.chown(self.pidfile, uid, gid)
            os.setgid(gid)
            os.setuid(uid)

        if not haspid and os.path.isfile(self.pidfile):
            print("Starting daemon with pidfile: {0}".format(self.pidfile))

    def run(self):
        try:
            server = pywsgi.WSGIServer((self.hostname, self.port), self.app)
            server.serve_forever()
        except Exception as e:
            print("Could not start server: {0}".format(e))

    def status(self):
        try:
            with open(self.pidfile, 'r') as fp:
                pid = int(fp.read())
            os.kill(pid, 0)
            print("Decanter is running, pidfile: {0}, process: {0}".format(self.pidfile, pid))
        except (OSError, IOError):
            print("Decanter is not running")

def usage():
    print("usage: {0} -h hostname -p port -c config.module start|stop|restart|status".format(sys.argv[0]))


if __name__ == '__main__':
    try:
        if len(sys.argv) == 8:
            command = sys.argv.pop()

            hostname = sys.argv[sys.argv.index('-h') + 1]
            port = int(sys.argv[sys.argv.index('-p') + 1])
            config = Config(sys.argv[sys.argv.index('-c') + 1])

            app = Dispatcher(StripPath(bottle.default_app()), config)
            pidfile = config.pidfile.format(port)
            logfile = config.logger['filepath'].format(port, date.today())
            # initialize logger
            log = Log(logfile)
            decanter = Decanter(app, hostname, port, pidfile)
            if 'start' == command:
                decanter.start()
            elif 'stop' == command:
                decanter.stop()
            elif 'status' == command:
                decanter.status()
            elif 'restart' == command:
                decanter.restart()
            else:
                usage()
        else:
            usage()
    except ValueError:
        usage()
