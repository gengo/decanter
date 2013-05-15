#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import popen2
import sys
sys.path.append('decanter')
import decanter


class Tests(unittest.TestCase):

    """
    How to perform the test the difference, because the program is to be
    terminated when it failed.
    """
    def is_error_occurred(self, arg):
        command = 'python test_parse_args.py {0}'.format(arg)
        stderr = popen2.popen3(command)[2]

        return not len(stderr.readline()) == 0

    def test_insufficient_arguments(self):
        self.assertTrue(self.is_error_occurred('-p 9000 -h localhost'))

    def test_port_is_not_integer(self):
        self.assertTrue(self.is_error_occurred('-p abc -c decanter.py'))

    def test_config_file_does_not_exist(self):
        self.assertTrue(self.is_error_occurred(
            '-c this_is_a_file_that_does_not_exist.txt'))

    def test_parse_result(self):
        # short ver
        args = 'decanter -c test_runner.py -h example.com -p 8000 start'.split(
        )
        result = decanter.parse_args(args)
        self.assertEqual(result.config, '../test_runner.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')

        # change arguments
        args = 'decanter -c test_runner.py -h foo.bar -p 8080 stop'.split()
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'stop')

        # change order
        args = 'decanter status -p 8080 -h foo.bar -c test_runner.py'.split()
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'status')

        # omit arguments
        args = 'decanter -c test_runner.py restart'.split()
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'localhost')
        self.assertEqual(result.port, 9000)
        self.assertEqual(result.command, 'restart')

        # long ver
        args = 'decanter --config test_runner.py --hostname example.com --port 8000 start'.split(
        )
        result = decanter.parse_args(args)
        self.assertEqual(result.config, '../test_runner.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')

        # change arguments
        args = 'decanter --config test_runner.py --hostname foo.bar --port 8080 stop'.split(
        )
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'stop')

        # change order
        args = 'decanter status --port 8080 --hostname foo.bar --config test_runner.py'.split(
        )
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'foo.bar')
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.command, 'status')

        # omit arguments
        args = 'decanter --config test_runner.py restart'.split()
        result = decanter.parse_args(args)
        self.assertEqual(result.hostname, 'localhost')
        self.assertEqual(result.port, 9000)
        self.assertEqual(result.command, 'restart')

        # mix short and long
        args = 'decanter -c test_runner.py --hostname example.com -p 8000 start'.split(
        )
        result = decanter.parse_args(args)
        self.assertEqual(result.config, '../test_runner.py')
        self.assertEqual(result.hostname, 'example.com')
        self.assertEqual(result.port, 8000)
        self.assertEqual(result.command, 'start')
