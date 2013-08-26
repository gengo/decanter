#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import textwrap
import pwd
import grp
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
import bottle
from datetime import date
from vendor.daemon import Daemon
from lib.middleware import Dispatcher, StripPath, SessionWsgi
from lib.config import Config
import lib.plugin
from lib.logger import Log
import argparse

original_args = []


class Decanter(Daemon):

    def __init__(self, app, hostname='localhost', port=9000,
                 pidfile='/var/run/decanter.pid', development=False):
        self.app = app
        self.hostname = hostname
        self.port = int(port)
        self.pidfile = pidfile
        self.config = Config()

        if 'timezone' in self.config:
            os.environ['TZ'] = self.config.timezone

        # remove all default bottle plugins
        bottle.uninstall(True)
        bottle.DEBUG = self.config.debug
        # install plugins
        self.install(plugins=self.config.plugins)
        if self.config.debug or not development:
            stdout = os.popen('tty').read().strip()
            stderr = os.popen('tty').read().strip()

        if not development:
            super(Decanter, self).__init__(
                pidfile, stdout=stdout, stderr=stderr)

    def install(self, plugins=[]):
        third_party_plugin_dir = '/'.join([self.config.apppath, 'plugins'])
        third_party_plugin_module = '.'.join([
            self.config.apppath.strip(os.path.sep).split(os.path.sep).pop(),
            'plugins'])
        for plugin in plugins:
            name = ''.join([plugin.capitalize(), 'Plugin'])
            cls = getattr(lib.plugin, name, None)

            if not cls and os.path.isdir(third_party_plugin_dir):
                for plugin_file in os.listdir(third_party_plugin_dir):
                    if not plugin_file.endswith('.py'):
                        continue
                    module = __import__(
                        '.'.join([
                            third_party_plugin_module,
                            os.path.splitext(plugin_file)[0]]),
                        fromlist=[name])
                    cls = getattr(module, name, None)
                    if cls:
                        break

            if not cls:
                raise ImportWarning(name + ' is not found.')
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

        if not haspid and os.path.isfile(self.pidfile)\
                and not self.config.test:
            print("Starting daemon with pidfile: {0}".format(self.pidfile))

    def run(self):
        log = None if self.config.test else 'default'
        server = pywsgi.WSGIServer((
            self.hostname, self.port), self.app, log=log)
        server.serve_forever()

    def runserver(self):
        """
        Command to run for development environments.
        """
        print(textwrap.dedent("""
            {2}
            Welcome to Decanter!
            You're ready to go!
            Server running on http://{1}:{0}
            {2}""".format(self.port, self.hostname, '=' * 50)))
        try:
            self.run()
        except KeyboardInterrupt:
            # Don't show traceback when sending ^C during runserver
            print('\nGood-bye!')

    def status(self):
        try:
            with open(self.pidfile, 'r') as fp:
                pid = int(fp.read())
            os.kill(pid, 0)
            print("Decanter is running, pidfile: {0}, process: {1}".format(
                self.pidfile, pid))
        except (OSError, IOError):
            print("Decanter is not running")


def parse_args(filepath=__file__, source=sys.argv, custom_commands=[]):
    """
    This function will parse command line arguments. To display help and exit
    if the argument is invalid. Will return command, hostname, port and config.
    """
    global original_args
    original_args = sys.argv[:]

    defaults = {
        'myself': source.pop(0),
        'hostname': 'localhost',
        'port': 9000,
        'conf': 'app/config/settings.py'
    }
    if len(source) == 0:
        source.append(defaults['myself'])

    parser = argparse.ArgumentParser(
        description='Example: {myself} -h {hostname}' +
                    '-p {port} -c config/devel.py start'.format(
                        **defaults), conflict_handler='resolve')
    parser.add_argument('command', choices=[
                        'start', 'stop', 'restart', 'status', 'runserver'] + custom_commands)
    parser.add_argument('-h', '--hostname', default=defaults['hostname'])
    parser.add_argument('-p', '--port', type=int, default=defaults['port'])
    parser.add_argument(
        '-c', '--config', required=False, default=defaults['conf'], type=argparse.FileType(),
        help='config must match the location of a module containing' +
             'decanter required configuration items, i.e. app/config/settings.py')
    args = parser.parse_args(source)

    # 'type=argparse.FileType()' will confirm the existence of a file.
    # but it open file.
    args.config.close()
    args.config = os.path.relpath(os.path.realpath(args.config.name),
                                  os.path.dirname(os.path.realpath(filepath)))

    return args

if __name__ == '__main__':
    args = parse_args()

    # initialize Config
    config = Config(args.config)

    # the log file
    logfile = config.logger['filepath'].format(args.port, date.today())
    # the pid fle
    pidfile = config.pidfile.format(args.port)
    # initialize logger
    log = Log(logfile)

    # make directory to put pid file
    piddir = os.path.dirname(pidfile)
    if not os.path.isdir(piddir):
        os.makedirs(piddir)

    # the app
    app = Dispatcher(StripPath(SessionWsgi(bottle.app())), config)
    decanter = Decanter(
        app, hostname=args.hostname, port=args.port, pidfile=pidfile,
        development=args.command == 'runserver')

    # execute command
    {
        'start': lambda: decanter.start(),
        'stop': lambda: decanter.stop(),
        'status': lambda: decanter.status(),
        'restart': lambda: decanter.restart(),
        'runserver': lambda: decanter.runserver(),
    }[args.command]()
