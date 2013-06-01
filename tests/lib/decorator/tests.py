#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from subprocess import Popen, PIPE
import os
import shlex
import requests
import json


class Tests(unittest.TestCase):
    BASE_PATH = 'http://localhost:9000'

    @classmethod
    def assemble(cls, *source):
        return os.sep.join(part for part in source)

    @classmethod
    def operationOfServer(cls, operation):
        args = {
            'decanter': Tests.assemble('decanter', 'decanter.py'),
            'config': Tests.assemble('tests', 'lib', 'decorator', 'config.py'),
            'operation': operation
        }
        command = 'python {decanter} -c {config} {operation}'.format(**args)
        options = {'stdout': PIPE, 'stderr': PIPE, 'close_fds': True}

        process = Popen(shlex.split(command), **options)
        process.wait()

    @classmethod
    def setUpClass(cls):
        Tests.operationOfServer('start')

    @classmethod
    def tearDownClass(cls):
        Tests.operationOfServer('stop')

    def test_method_get(self):
        payload = {'param': 'get_test'}
        result = requests.get(
            Tests.BASE_PATH + '/method/path_of_get', params=payload).text
        expected = {'method': 'GET', 'path':
                    'path_of_get', 'param': 'get_test'}
        self.assertDictEqual(expected, json.loads(result))

    def test_method_post(self):
        payload = {'param': 'post_test'}
        result = requests.post(
            Tests.BASE_PATH + '/method/path_of_post', data=payload).text
        expected = {'method': 'POST', 'path':
                    'path_of_post', 'param': 'post_test'}
        self.assertDictEqual(expected, json.loads(result))

    def test_method_put(self):
        payload = {'param': 'put_test'}
        result = requests.put(
            Tests.BASE_PATH + '/method/path_of_put', data=payload).text
        expected = {'method': 'PUT', 'path':
                    'path_of_put', 'param': 'put_test'}
        self.assertDictEqual(expected, json.loads(result))

    def test_method_delete(self):
        payload = {'param': 'delete_test'}
        result = requests.delete(
            Tests.BASE_PATH + '/method/path_of_delete', params=payload).text
        expected = {'method': 'DELETE', 'path':
                    'path_of_delete', 'param': 'delete_test'}
        self.assertDictEqual(expected, json.loads(result))

    def test_apply_list(self):
        result = requests.get(Tests.BASE_PATH + '/apply_list').text
        expected = {'apply': 'list'}
        self.assertEqual(expected, json.loads(result))
