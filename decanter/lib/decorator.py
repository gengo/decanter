#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import json
import bottle
from bottle import request
import plugin as lib_plugin
from loaders import SchemaLoader
from errors import ValidationError

from jsonschema import validate
from jsonschema import ValidationError as JSONValidationError

def route(path=None, method='GET', func=None,
          name=None, apply=None, skip=None, **config):
    def decorator(callback):
        rpath = path
        plugins = []
        if isinstance(apply, str):
            cls = ''.join([apply.lower().capitalize(), 'Plugin'])
            cls = getattr(lib_plugin, cls)
            plugins.append(cls())
        elif isinstance(apply, list):
            for plugin in apply:
                cls = ''.join([plugin.lower().capitalize(), 'Plugin'])
                cls = getattr(lib_plugin, cls)
                plugins.append(cls())

        if rpath != '/':
            rpath = rpath.rstrip('/')

        callback = bottle.route(
            path=rpath, method=method, callback=func, name=name,
            apply=plugins, skip=skip, **config)(callback)

        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def _wrap(path, method, **kwargs):
    def decorator(callback):
        callback = route(path=path, method=method, **kwargs)(callback)

        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def get(path=None, **kwargs):
    return _wrap(path=path, method='GET', **kwargs)


def post(path=None, **kwargs):
    return _wrap(path=path, method='POST', **kwargs)


def put(path=None, **kwargs):
    return _wrap(path=path, method='PUT', **kwargs)


def delete(path=None, **kwargs):
    return _wrap(path=path, method='DELETE', **kwargs)


def validate_schema(schema=None, **kwargs):
    """
    Validate input according to some JSON-schema file, 
    and return an error object if there is a problem.
    """
    def decorator(callback):
        print "Validating schema", schema
        
        rules = SchemaLoader.get_instance().load_template(schema)
        if not rules:
            raise ValidationError(message="Validation schema not found.", fields=[])

        @wraps(callback)
        def wrapper(*args, **kwargs):
            try:
                obj = request.forms
                obj = dict(request.forms)
                validate(obj, json.loads(rules))
            except JSONValidationError:
                callback = bottle.route(
                    path='/json/error', method=method, callback=func, name=name,
                    apply=plugins, skip=skip, **config)(callback)

            return callback(*args, **kwargs)
        return wrapper
    return decorator
