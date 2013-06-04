#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import subprocess
import os
import shlex
import requests
import json
import socket


class Tests(unittest.TestCase):

    def find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', 0))
        address, port = s.getsockname()
        s.close()
        return port

    def assemble(self, *source):
        return os.sep.join(part for part in source)

    def operationOfServer(self, operation):
        args = {
            'decanter': self.assemble('decanter', 'decanter.py'),
            'config': self.assemble('tests', 'lib', 'decorator', 'config.py'),
            'port': self.port,
            'operation': operation
        }
        command = 'python {decanter} -c {config} -p {port} {operation}'.format(**args)
        subprocess.call(shlex.split(command))

    def setUp(self):
        self.port = self.find_free_port()
        self.base_path = 'http://localhost:{0}'.format(self.port)
        self.operationOfServer('start')

    def tearDown(self):
        self.operationOfServer('stop')

    def test_method_get(self):
        payload = {'param': 'get_test'}
        result = requests.get(
            self.base_path + '/method/path_of_get', params=payload).text
        expected = {'method': 'GET', 'path':
                    'path_of_get', 'param': 'get_test'}
        self.assertEqual(expected, json.loads(result))

    def test_method_post(self):
        payload = {'param': 'post_test'}
        result = requests.post(
            self.base_path + '/method/path_of_post', data=payload).text
        expected = {'method': 'POST', 'path':
                    'path_of_post', 'param': 'post_test'}
        self.assertEqual(expected, json.loads(result))

    def test_method_put(self):
        payload = {'param': 'put_test'}
        result = requests.put(
            self.base_path + '/method/path_of_put', data=payload).text
        expected = {'method': 'PUT', 'path':
                    'path_of_put', 'param': 'put_test'}
        self.assertEqual(expected, json.loads(result))

    def test_method_delete(self):
        payload = {'param': 'delete_test'}
        result = requests.delete(
            self.base_path + '/method/path_of_delete', params=payload).text
        expected = {'method': 'DELETE', 'path':
                    'path_of_delete', 'param': 'delete_test'}
        self.assertEqual(expected, json.loads(result))

    def test_apply_list(self):
        result = requests.get(self.base_path + '/apply_list').text
        expected = {'apply': 'list'}
        self.assertEqual(expected, json.loads(result))
