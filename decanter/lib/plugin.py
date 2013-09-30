#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import gettext
import traceback
from functools import wraps
from jinja2 import BaseLoader
from jinja2 import Environment
from jinja2 import ChoiceLoader
from jinja2 import FileSystemLoader
from jinja2 import TemplateNotFound
from bottle import request, response, PluginError
from .logger import Log
from .config import Config
from .errors import BaseError, ValidationError, ConnectionError

# Format of http.request.header.Accept-Language.
# refs: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
REQUEST_ACCEPT_LANGUAGE_RE = re.compile(r'''
        ([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*|\*)   # "en", "en-au", "*"
        (?:;q=(0(?:\.\d{,3})?|1(?:.0{,3})?))?   # Optional "q=1.00", "q=0.8"
        (?:\s*,\s*|$)                           # Multiple accepts per header.
        ''', re.VERBOSE)


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
            self.config = Config()
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
                                     DecanterLoader(basepath)]))

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


class Jinja2i18nPlugin(Jinja2Plugin):
    __state = {}
    name = 'jinja2i18n'
    api = 2

    def __init__(self):
        super(Jinja2i18nPlugin, self).__init__()

        config = Config()
        self.domain = getattr(config, 'domain', 'locale')
        locale_dir = getattr(config, 'locale_dir')
        lang_code = getattr(config, 'lang_code', 'en')

        if locale_dir is None:
            locale_dir = os.path.normpath(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'locale'))
        if not os.path.exists(locale_dir):
            raise PluginError(
                'No locale directory found, please assign a right one.')
        self.locale_dir = locale_dir
        self.lang_code = lang_code
        self.prepared = {}
        self.app = None
        self.trans = None

    def setup(self, app):
        self.app = app
        self.app._ = lambda s: s
        self.app.set_lang = self.prepare
        self.app.hooks.add('before_request', self.prepare)

    def extra_client_expected_langs(self):
        """Return language list from http.request.header.Accept-Language, ordered by 'q'."""
        result = []
        pieces = REQUEST_ACCEPT_LANGUAGE_RE.split(
            request.headers.get('Accept-Language', ''))
        if pieces[-1]:
            return []
        for i in range(0, len(pieces) - 1, 3):
            first, lang, priority = pieces[i: i + 3]
            if lang == '*':  # TODO: support default language
                return []
            if first:
                return []
            priority = priority and float(priority) or 1.0
            result.append((lang, priority))
        result.sort(key=lambda k: k[1], reverse=True)
        return result

    def get_language_list(self):
        expected_langs = self.extra_client_expected_langs()

        lang_codes = []

        for lang, priority in expected_langs:
            lang_country = lang.split('-')
            if len(lang_country) == 1:
                lang_codes.append(lang)
                continue
            country = lang_country[1]
            lang_codes.append('%s_%s' % (lang_country[0], country))
            lang_codes.append('%s_%s' % (lang_country[0], country.swapcase()))

        if not self.lang_code is None:
            lang_codes += [self.lang_code]

        return lang_codes

    def prepare(self, langs=None):
        if langs is None:
            langs = self.get_language_list()
        prepared_key = tuple(langs)
        if prepared_key in self.prepared:
            trans = self.prepared.get(prepared_key)
            if trans:
                trans.install(True)
                self.app._ = trans.ugettext
            else:
                self.app._ = lambda s: s

            self.trans = trans
            return

        try:
            trans = gettext.translation(
                self.domain, self.locale_dir, languages=langs)
            trans.install(True)
            self.app._ = trans.ugettext
            self.prepared[prepared_key] = trans
        except Exception:
            Log.get_instance().error("No locale folder found for translations or problems with importing it.")
            trans = None
            self.app._ = lambda s: s
            self.prepared[prepared_key] = None

        self.trans = trans

    def apply(self, callback, route):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if self.name in route.skiplist:
                return callback(*args, **kwargs)

            self.prepare()

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

            # add i18n variables
            data = callback(*args, **kwargs)
            data['_'] = self.app._
            data['ngettext'] = self.trans.ungettext

            return tpl.render(data)

        return wrapper


class JsonPlugin(object):
    name = 'json'
    api = 2

    def apply(self, callback, route):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            config = Config()
            if self.name in route.skiplist:
                return callback(*args, **kwargs)

            try:
                data = callback(*args, **kwargs)
            # catch validation errors from the controller
            except (BaseError, ValidationError, ConnectionError, Exception) as e:
                # create a standardized error object
                data = {
                    'opstat': 'error'
                }
                if hasattr(e, 'message') and e.message:
                    data['error'] = e.message
                elif hasattr(e, 'msg') and e.msg:
                    data['error'] = e.msg
                else:
                    data['error'] = unicode(e)
                if hasattr(e, 'fields') and isinstance(e.fields, dict):
                    data['fields'] = e.fields
                if hasattr(e, 'returned') and isinstance(e.returned, dict):
                    data['response'] = e.returned

                if not isinstance(e, ValidationError):
                    Log.get_instance().error(
                        "Error tracked: \Request: %s\nMessage: %s\nFields: %s\nResponse: %s\n\nTraceback: %s" % (
                            request,
                            e.message,
                            getattr(e, 'fields', None),
                            getattr(e, 'response', None),
                            traceback.format_exc()
                        )
                    )
                    # return server error response
                    response.status = 500

                if config.debug is True:
                    data['traceback'] = traceback.format_exc()

            response.set_header('Content-Type', 'application/json')
            return json.dumps(data)

        return wrapper

    def setup(self, app):
        pass

    def close(self):
        pass


class SessionPlugin(object):
    name = 'session'
    api = 2

    def __init__(self):
        pass

    def apply(self, callback, route):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if self.name in route.skiplist:
                return callback(*args, **kwargs)
            data = callback(*args, **kwargs)
            if 'express.session' in request.environ:
                request.environ['express.session'].write()
                # session does not need to be close or released as
                # StrictRedis releases the connection after each operation
            return data
        return wrapper

    def setup(self, app):
        pass

    def close(self):
        pass
