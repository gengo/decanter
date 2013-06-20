#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from config import Config


class Redis(object):

    """
    Borg Pattern
    """
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state
        if '_redis' not in self.__dict__:
            config = Config.get_instance()

            pool = redis.ConnectionPool(db=config.redis.get('db', 0),
                                        host=config.redis.get(
                                            'host', 'localhost'),
                                        port=config.redis.get('port', 6379),
                                        max_connections=config.redis.get('max_poolsize', 5))
            self._redis = redis.StrictRedis(connection_pool=pool)

    def __getattr__(self, name):
        return getattr(self._redis, name)
