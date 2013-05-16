#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import gettext
from functools import wraps
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import TemplateNotFound
from jinja2 import BaseLoader
from jinja2 import ChoiceLoader
from config import Config
from bottle import response


class DecanterLoader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        template = template.lstrip('/')
        bundle = template.partition('/')
        filepath = os.path.join(self.path, bundle[0], 'views', bundle[2])
        if os.path.isabs(filepath) and os.path.isfile(filepath):
            mtime = os.path.getmtime(filepath)
            with file(filepath) as f:
                source = f.read().decode('utf-8')
            return (source,
                    filepath,
                    lambda: mtime == os.path.getmtime(filepath))
        raise TemplateNotFound(template)


class Jinja2Plugin(object):
    __state = {}
    name = 'jinja2'
    api = 2

    def __init__(self):
        """ Borg Pattern """
        self.__dict__ = self.__state
        if 'env' not in self.__dict__:
            self.config = Config.get_instance()
            basepath = os.path.join(self.config.apppath, 'bundles')
            bundels = [name for name in os.listdir(
                basepath) if os.path.isdir(os.path.join(basepath, name))]
            views = []

            for bundle in bundels:
                if bundle != 'views':
                    views.append(os.path.join(basepath, bundle, 'views'))

            # add views directory in bundle
            if 'views' in bundels:
                views.append(os.path.join(basepath, 'views'))

            self.env = Environment(
                loader=ChoiceLoader([FileSystemLoader(views, encoding='utf-8'),
                                     DecanterLoader(
                                     basepath)]),
                extensions=['jinja2.ext.i18n'])
            self.env.install_gettext_translations(gettext.NullTranslations())

    def apply(self, callback, route):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if self.name in route.skiplist:
                return callback(*args, **kwargs)

            data = callback(*args, **kwargs)
            if not isinstance(data, dict):
                return data

            bundle = callback.__module__.split('.')[-3]
            controller = callback.__module__.split('.')[-1]
            action = callback.__name__
            template = os.path.join(
                bundle, controller, '.'.join([action, 'html']))
            try:
                tpl = self.env.get_template(template)
            except TemplateNotFound:
                template = os.path.join(controller, '.'.join([action, 'html']))
                tpl = self.env.get_template(template)
            return tpl.render(data)

        return wrapper

    def setup(self, app):
        pass

    def close(self):
        pass


class JsonPlugin(object):
    name = 'json'
    api = 2

    def apply(self, callback, route):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if self.name in route.skiplist:
                return callback(*args, **kwargs)

            data = callback(*args, **kwargs)
            response.set_header('Content-Type', 'application/json')
            return json.dumps(data)

        return wrapper

    def setup(self, app):
        pass

    def close(self):
        pass
