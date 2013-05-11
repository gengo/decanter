#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from config import *
from singleton import Singleton


class Config(Singleton):
    def __init__(self, config=None):
        """
        module (str): name of a python module or path to the file containing
        configuration parameters
        """
        if getattr(self, '__init', False):
            # do initialization here
            self.__data = self._load(config)

    def _load(self, config):
        if config.endswith('.py'):
            config = '.'.join(config.rsplit('.py')[0].strip(os.path.sep).
                              split(os.path.sep))
        segs = config.rsplit('.')
        name = segs.pop() if len(segs) > 1 else None
        if name:
            return __import__(config, fromlist=[name])
        else:
            return __import__(config)

    def __getattr__(self, name):
        return getattr(self.__data, name, None)

    def __getitem__(self, name):
        return getattr(self.__data, name, None)

    def __contains__(self, name):
        return hasattr(self.__data, name)
