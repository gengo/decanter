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
from bottle import request, response
from errors import BaseError, ValidationError, ConnectionError

from logger import Log


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
                    baseViews = os.path.join(basepath, bundle, 'views')
                    if os.path.isdir(baseViews):
                        views.append(baseViews)

            # add views directory in bundle
            if 'views' in bundels:
                views.append(os.path.join(basepath, 'views'))

            # add app/views directory
            views.append(os.path.join(self.config.apppath, 'views'))

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

            try:
                data = callback(*args, **kwargs)
            # catch validation errors from the controller
            except (BaseError, ValidationError, ConnectionError), e:
                # create a standardized error object
                data = {
                    'opstat': 'error'
                }
                if e.message:
                    data['error'] = e.message
                if hasattr(e, 'fields') and isinstance(e.fields, dict):
                    data['fields'] = e.fields.keys()
                    data.update(e.fields)
                if hasattr(e, 'returned') and isinstance(e.returned, dict):
                    data['response'] = e.returned

                Log.get_instance().debug(
                    "Error tracked: \Request: %s\nMessage: %s\nFields: %s\nResponse: %s\n" % (
                        request,
                        e.message,
                        getattr(e, 'fields', None),
                        getattr(e, 'response', None))
                )

                if Config.get_instance().debug:
                    print "Error tracked:\n==========="
                    print e
                    print "Message:", e.message
                    print "Fields:", getattr(e, 'fields', None)
                    print "Response:", getattr(e, 'response', None)

            response.set_header('Content-Type', 'application/json')
            return json.dumps(data)

        return wrapper

    def setup(self, app):
        pass

    def close(self):
        pass
