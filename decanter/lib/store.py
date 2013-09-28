#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from config import Config


class Redis(object):
    """ Borg Pattern
    one state many objects useful in this case as we
    want one pool but many objects
    """
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state
        if '_pool' not in self.__dict__:
            config = Config()
            # we only need one pool per app
            self._pool = redis.ConnectionPool(db=config.redis.get('db', 0),
                                              host=config.redis.get('host', 'localhost'),
                                              port=config.redis.get('port', 6379),
                                              max_connections=config.redis.get('max_poolsize', 10))

        # each object required its own connection so that we can close
        # it after each request without affecting other requests
        #
        # so this line is NOT within the above if statement
        self._redis = redis.StrictRedis(connection_pool=self._pool)

    def __getattr__(self, name):
        return getattr(self._redis, name)
