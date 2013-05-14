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
import argparse


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
            # Such a message is noise during test.
            # 127.0.0.1 - - [yyyy-MM-dd HH:mm:ss] ...
            log = None if self.config.test else 'default'
            server = pywsgi.WSGIServer((self.hostname, self.port), self.app, log=log)
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


def parse_args(source=sys.argv):
    """
    This function will parse command line arguments. To display help and exit
    if the argument is invalid. Will return command, hostname, port and config.
    """
    defaults = {
        'myself': source.pop(0),
        'hostname': 'localhost',
        'port': 9000
    }
    if len(source) == 0:
        source.append(defaults['myself'])

    parser = argparse.ArgumentParser(description='Example: {myself} -h {hostname} -p {port} -c config/devel.py start'.format(**defaults), conflict_handler='resolve')
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status'])
    parser.add_argument('-h', '--hostname', default=defaults['hostname'])
    parser.add_argument('-p', '--port', type=int, default=defaults['port'])
    parser.add_argument('-c', '--config', required=True, type=argparse.FileType(), help='config must match the location of a module containing decanter required configuration items, i.e. config/devel.py')
    args = parser.parse_args(source)

    # 'type=argparse.FileType()' will confirm the existence of a file. but it open file.
    args.config.close()
    args.config = os.path.relpath(os.path.realpath(args.config.name),
                                  os.path.dirname(os.path.realpath(__file__)))

    return args

if __name__ == '__main__':
    args = parse_args()

    config = Config(args.config)
    app = Dispatcher(StripPath(bottle.default_app()), config)
    pidfile = config.pidfile.format(args.port)

    # make directory to put pid file
    piddir = os.path.dirname(pidfile)
    if not os.path.isdir(piddir):
        os.makedirs(piddir)

    logfile = config.logger['filepath'].format(args.port, date.today())
    # initialize logger
    log = Log(logfile)
    decanter = Decanter(app, args.hostname, args.port, pidfile)

    # execute command
    {
        'start': lambda: decanter.start(),
        'stop': lambda: decanter.stop(),
        'status': lambda: decanter.status(),
        'restart': lambda: decanter.restart()
    }[args.command]()
