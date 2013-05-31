#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.decorator import get, post, put, delete
from bottle import request


def _format(path):
    return {'method': request.method, 'path': path, 'param': request.params.get('param')}


@get('/method/<path>', apply='json')
def get(path):
    return _format(path)


@post('/method/<path>', apply='json', skip='jinja2')
def post(path):
    return _format(path)


@put('/method/<path>', apply='json', skip='jinja2')
def put(path):
    return _format(path)


@delete('/method/<path>', apply='json', skip='jinja2')
def delete(path):
    return _format(path)
