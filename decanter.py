#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
import bottle
from vendor.daemon import Daemon


class Decanter(Daemon):
    def __init__(self, app, hostname='localhost', port=9000, pidfile = None):
        self.app = app
        self.hostname = hostname
        self.port = int(port)
        # TODO: import settings some how, or Config class
        super(Daemon, self).__init__(pidfile)

    def run():
        try:
            server = pywsgi.WSGIServer((self.hostname, self.port), self.app)
            server.serve_forever()
        except Exception as e:
            print("Could not start server: {0}".format(e))



if __name__ == '__main__':
    decanter = Decanter(bottle.default_app())
    decanter.start()
