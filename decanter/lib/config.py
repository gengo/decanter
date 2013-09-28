#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from singleton import Singleton
import sys


class Config(Singleton):

    def __init__(self, config=None):
        """
        config (str): name of a python module or path to the file containing
        configuration parameters
        """
        self.__data = self._load(config)

    def _load(self, config):
        parent_count = 0
        while config.startswith('../'):
            config = config[3:]
            parent_count += 1
        if config.endswith('.py'):
            config = '.'.join(config.rsplit('.py')[0].strip(os.path.sep).
                              split(os.path.sep))

        if parent_count != 0:
            base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            for i in range(0, parent_count):
                base = os.path.dirname(base)
            sys.path.insert(0, base)

        segs = config.rsplit('.')
        name = segs.pop() if len(segs) > 1 else None
        if name:
            module = __import__(config, fromlist=[name])
        else:
            module = __import__(config)

        if parent_count != 0:
            sys.path.pop(0)

        return module

    def __getattr__(self, name):
        return getattr(self.__data, name, None)

    def __getitem__(self, name):
        return getattr(self.__data, name, None)

    def __contains__(self, name):
        return hasattr(self.__data, name)
