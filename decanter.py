#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
import bottle
from vendor.daemon import Daemon
from lib.middleware import Dispatcher
from lib.middleware import StripPath
from lib.config import Config
import lib.plugin


class Decanter(Daemon):
    def __init__(self, app, hostname='localhost', port=9000, pidfile = '/var/run/decanter.pid'):
        self.app = app
        self.hostname = hostname
        self.port = int(port)
        # remove all bottle templates by default
        bottle.uninstall(True)
        config = Config.get_instance()
        self.install(plugins=config.plugins)
        if config.debug:
            stdout = os.popen('tty').read().strip()
            stderr = os.popen('tty').read().strip()

        super(Decanter, self).__init__(pidfile, stdout=stdout, stderr=stderr)

    def install(self, plugins=[]):
        for plugin in plugins:
            name = ''.join([plugin.lower().capitalize(), 'Plugin'])
            cls = getattr(lib.plugin, name)
            bottle.install(cls())

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
    print("usage: {0} config.module start|stop|restart|status".format(sys.argv[0]))


if __name__ == '__main__':
    try:
        if len(sys.argv) == 3:
            command = sys.argv.pop()
            config = Config(sys.argv[1])
            app = Dispatcher(StripPath(bottle.default_app()), config)
            port = int(config.port)
            hostname = config.hostname
            pidfile = config.pidfile.format(port)
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
    except Exception as e:
        print("Error: {0}".format(e))
