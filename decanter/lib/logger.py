#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
from config import Config


class Log(object):
    __state = {}
    """
    simple logging.Logger wrapper
    """
    def __init__(self, filepath='/var/log/decanter.log'):
        """ Borg pattern """
        self.__dict__ = self.__state
        if '_log' not in self.__dict__:
            config = Config()
            if 'filepath' in config.logger:
                self.filepath = config.logger['filepath']
            else:
                self.filepath = filepath
            try:
                handler = logging.handlers.TimedRotatingFileHandler(
                    self.filepath, 'midnight', 1, 10, 'UTF-8')
            except IOError:
                # check if log directory exists
                parent_path = parent_path = os.path.abspath(
                    os.path.dirname(self.filepath))
                if not os.path.exists(parent_path):
                    # try to create the logs directory
                    os.makedirs(parent_path, mode=0o755)
                # and try again
                handler = logging.handlers.TimedRotatingFileHandler(
                    self.filepath, 'midnight', 1, 10, 'UTF-8')

            formatter = logging.Formatter('%(levelname)s - %(asctime)s - ' +
                                          'File:%(pathname)s - Line:' +
                                          '%(lineno)d - Func:' +
                                          '%(funcName)s\n%(message)s')

            handler.setLevel(config.logger['level'])
            handler.setFormatter(formatter)
            self._log = logging.getLogger(__name__)
            self._log.setLevel(config.logger['level'])
            self._log.addHandler(handler)

    @classmethod
    def get_instance(self):
        return self()

    def critical(self, msg, *args, **kwargs):
        self._log.critical(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log.error(msg, *args, **kwargs)

    def exception(self, msg, *args):
        self._log.exception(msg, *args)

    def info(self, msg, *args, **kwargs):
        self._log.info(msg, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._log, name)
