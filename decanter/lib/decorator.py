#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gettext import gettext as _
from functools import wraps
import bottle
from bottle import request, redirect
import plugin as lib_plugin
from errors import ValidationError
from . import jsonvalidation


def route(path=None, method='GET', func=None, name=None, apply=None, skip=None, **config):
    def decorator(callback):
        plugins = []

        def apply_plugin(plugin):
            cls = ''.join([plugin.capitalize(), 'Plugin'])
            cls = getattr(lib_plugin, cls)
            plugins.append(cls())

        if isinstance(apply, str):
            apply_plugin(apply)
        elif isinstance(apply, list):
            for plugin in apply:
                apply_plugin(plugin)

        rpath = path
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


def get(path=None, **kwargs):
    return route(path=path, method='GET', **kwargs)


def post(path=None, **kwargs):
    return route(path=path, method='POST', **kwargs)


def put(path=None, **kwargs):
    return route(path=path, method='PUT', **kwargs)


def delete(path=None, **kwargs):
    return route(path=path, method='DELETE', **kwargs)


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
            if request.headers.get("Content-Type") in ("application/json", "application/javascript", "text/javascript"):
                data = request.json
                instance = data
            else:
                data = request.forms
                data.update(request.query)
                instance = convert_to_dict(data)
            request.cleaned_data = instance
            errors = jsonvalidation.get_error_dictionary(
                schema=schema, instance=instance)
            if errors:
                raise ValidationError(
                    message=_("There were errors validating your request."),
                    fields=errors)
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def login_required(login_url=None, login_id='user_id'):
    '''
    Checks if 'login_id' attribute is present in the session,
    and redirects to 'login_url' if it's not.
    '''
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            session = request.environ['express.session']
            if login_id not in session:
                if login_url:
                    redirect(login_url)
                else:
                    raise Exception('Login Required')
                return {}
            return callback(*args, **kwargs)
        return wrapper
    return decorator
