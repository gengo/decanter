#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import bottle
from lib.config import Config


@bottle.error(500)
def error_500(error):
    config = Config()
    accept = bottle.request.headers.get('accept', False)
    is_json = accept and 'json' in accept
    if config.debug and is_json:
        return json.dumps({'status': 500, 'error': error.traceback})
    elif config.debug:
        return bottle.template(bottle.ERROR_PAGE_TEMPLATE, {'e': error})
    elif is_json:
        return json.dumps({'status': 500, 'error': error.body})
    return bottle.template(bottle.ERROR_PAGE_TEMPLATE, {'e': error})
