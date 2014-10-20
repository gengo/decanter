#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from subprocess import Popen, PIPE
import decanter.decanter as decanter
import shlex


class Tests(unittest.TestCase):

    """
    How to perform the test the difference, because the program is to be
    terminated when it failed.
    """

    def is_error_occurred(self, arg):
        command = 'python test_parse_args.py {0}'.format(arg)
        options = {'stdout': PIPE, 'stderr': PIPE, 'close_fds': True}

        process = Popen(shlex.split(command), **options)
        process.wait()
        return not process.returncode == 0

    def test_insufficient_arguments(self):
        self.assertTrue(self.is_error_occurred('-p 9000 -h localhost'))

    def test_port_is_not_integer(self):
        self.assertTrue(self.is_error_occurred('-p abc -c decanter.py'))

    def test_config_file_does_not_exist(self):
        self.assertTrue(self.is_error_occurred(
            '-c this_is_a_file_that_does_not_exist.txt'))

    def test_parse_result(self):
        # short ver
        args = shlex.split('decanter -c setup.py \
-h example.com -p 8000 start')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.config, 'setup.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')

        # change arguments
        args = shlex.split('decanter -c setup.py \
-h foo.bar -p 8080 stop')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'stop')

        # change order
        args = shlex.split('decanter status -p 8080 \
-h foo.bar -c setup.py')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'status')

        # omit arguments
        args = shlex.split('decanter -c setup.py restart')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'localhost')
        self.assertEqual(result.port, 9000)
        self.assertEqual(result.command, 'restart')

        # long ver
        args = shlex.split('decanter --config setup.py \
--hostname example.com --port 8000 start')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.config, 'setup.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')

        # change arguments
        args = shlex.split('decanter --config setup.py \
--hostname foo.bar --port 8080 stop')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'stop')

        # change order
        args = shlex.split('decanter status --port 8080 \
--hostname foo.bar --config setup.py')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'status')

        # omit arguments
        args = shlex.split('decanter --config setup.py restart')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.hostname, 'localhost')
        self.assertEqual(result.port, 9000)
        self.assertEqual(result.command, 'restart')

        # mix short and long
        args = shlex.split('decanter -c setup.py \
--hostname example.com -p 8000 start')
        result = decanter.parse_args(source=args)
        self.assertEqual(result.config, 'setup.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')
