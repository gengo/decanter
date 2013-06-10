#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes for loading views and JSON schemas, etc
"""

import os
import codecs
from singleton import Singleton


class BaseLoader(Singleton):

    def __init__(self, config=None):
        """
        Uses the Singleton pattern, so that we can have subclasses
        maintain their own state.
        """
        if getattr(self, '__init', False):
            self.__data = self._load_state(config)

    def __getattr__(self, name):
        return self.__data.get(name, None)

    def __getitem__(self, name):
        return self.__data.get(name, None)

    def __contains__(self, name):
        return name in self.__data

    def _load_state(self, config):
        """
        Method to load the store (for subclasses to override).
        """
        raise NotImplemented()


class JSONLoader(BaseLoader):

    def _load_state(self, config):
        """
        Find all JSON-schema files in the directory structure
        and save them in this state storage.
        """
        data = {}
        path = os.path.join(config.apppath, 'bundles')

        # find all 'validations' folders:
        folders = {}
        for root, dirs, files in os.walk(path):
            validations = filter(lambda f: f == 'validations', dirs)
            folders.update(dict((f, []) for f in map(
                lambda f: os.path.join(root, f), validations)))

        # list all files in these folders
        for k, folder in folders.items():
            for root, dirs, files in os.walk(k):
                files = filter(lambda f: f.endswith('.json'), files)
                folder += map(lambda f: os.path.join(
                    os.path.relpath(root, k), f), files)

        data['directories'] = folders

        return data

    def load_template(self, path):
        rel_path = path
        for full_path, directory in self.directories.items():
            if rel_path in directory:
                return codecs.open(os.path.join(full_path, path), 'r', 'utf-8').read()
        return None
