#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseSingleton(type):
    """
    Need to write this because supports both Python 2.x and 3.x.

    class SubClass(with_metaclass('SubClass', Singleton)):
        pass
    """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(BaseSingleton, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]


# Hide how to write a complex inheritance
class Singleton(BaseSingleton('Singleton', (object, ), {})):
    """
    It becomes Singleton When class inherit this.
    """
    pass
