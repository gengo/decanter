#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Singleton(object):
    __instance = {}

    def __new__(cls, *args, **kwargs):
        if cls.__name__ not in cls.__instance:
            cls.__instance[cls.__name__] = super(cls.__class__, cls).__new__(cls, *args, **kwargs)
            setattr(cls.__instance[cls.__name__], '__init', True)
        else:
            setattr(cls.__instance[cls.__name__], '__init', False)
        return cls.__instance[cls.__name__]

    def __init__(self, *args, **kwargs):
        if getattr(self, '__init', False):
            # do initialization here
            pass

    @classmethod
    def get_instance(cls, *args, **kwargs):
        try:
            return cls.__instance[cls.__name__]
        except KeyError:
            return cls(*args, **kwargs)
