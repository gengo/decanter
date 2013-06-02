#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gettext import gettext as _
from functools import wraps
import bottle
from bottle import request
import plugin as lib_plugin
from errors import ValidationError
from . import jsonvalidation


def route(path=None, method='GET', func=None, name=None, apply=None, skip=None, **config):
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


def validate_schema(schema, **kwargs):
    """
    Validate input according to some JSON-schema file,
    and return an error object if there is a problem.
    """
    def decorator(callback):
        def convert_to_dict(bottle_form):
            """
            Function for converting a bottle multiple non-unique keys
            dictionary to a normal python dictionary with lists automatically
            created where appropriate, according to the JSON schema.
            """
            d = {}
            for key, value in bottle_form.iterallitems():
                if key not in d:
                    d[key] = value
                    if key in schema.get('properties') and not isinstance(value, list):
                        if 'array' == schema['properties'][key].get('type') or 'array' in schema['properties'][key].get('type'):
                            d[key] = [value]
                else:
                    if isinstance(d[key], list):
                        d[key] += [value]
                    else:
                        d[key] = [d.get(key)] + [value]
            return d

        @wraps(callback)
        def wrapper(*args, **kwargs):
            instance = convert_to_dict(request.forms)
            request.forms.as_dict = instance
            errors = jsonvalidation.get_error_dictionary(
                schema=schema, instance=instance)
            if errors:
                raise ValidationError(
                    message=_("There were errors validating your request."),
                    fields=errors)
            return callback(*args, **kwargs)
        return wrapper
    return decorator
