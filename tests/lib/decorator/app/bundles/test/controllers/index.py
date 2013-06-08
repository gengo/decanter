#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.decorator import get, post, put, delete, route
from bottle import request


def _format(path):
    return {
        'method': request.method,
        'path': path,
        'param': request.params.get('param')
    }


@get('/method/<path>', apply='json')
def get(path):
    return _format(path)


@post('/method/<path>', apply='json')
def post(path):
    return _format(path)


@put('/method/<path>', apply='json')
def put(path):
    return _format(path)


@delete('/method/<path>', apply='json')
def delete(path):
    return _format(path)


@route('/apply_list', apply=['json'])
def apply_list():
    return {'apply': 'list'}
