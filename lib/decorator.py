#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import bottle
import lib.plugin


def route(path=None, method='GET', func=None, name=None, apply=None, skip=None, **config):
    def decorator(callback):
        rpath = path
        plugins = []
        if isinstance(apply, str):
            cls = ''.join([apply.lower().capitalize(), 'Plugin'])
            cls = getattr(lib.plugin, cls)
            plugins.append(cls())
        elif isinstance(apply, list):
            for plugin in apply:
                cls = ''.join([apply.lower().capitalize(), 'Plugin'])
                cls = getattr(lib.plugin, cls)
                plugins.append(cls())

        if rpath != '/':
            rpath = rpath.rstrip('/')

        callback = bottle.route(path=rpath, method=method, callback=func, name=name,
                                apply=plugins, skip=skip, **config)(callback)
        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def get(path=None, **kwargs):
    def decorator(callback):
        callback = route(path=path, method='GET', **kwargs)(callback)
        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def post(path=None, **kwargs):
    def decorator(callback):
        callback = route(path=path, method='POST', **kwargs)(callback)
        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def put(path=None, **kwargs):
    def decorator(callback):
        callback = route(path=path, method='PUT', **kwargs)(callback)
        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
    return decorator
