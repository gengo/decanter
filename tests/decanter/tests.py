#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from subprocess import Popen, PIPE
import os
import shlex


class Tests(unittest.TestCase):

    def setUp(self):
        # . <- dir_of_original is here
        # ├── decanter
        # │   ├── config
        # │   └── decanter.py
        # ├── test_runner.py
        # └── tests
        self.dir_of_original = os.getcwd()

    def tearDown(self):
        os.chdir(self.dir_of_original)

    def is_error_occurred(self, args):
        command = 'python {decanter} -c {config} status'.format(**args)
        options = {'stdout': PIPE, 'stderr': PIPE, 'close_fds': True}

        process = Popen(shlex.split(command), **options)
        process.wait()
        return not process.returncode == 0

    def assemble(self, *source):
        # return 'path/to' if call assemble('path', 'to')
        return os.sep.join(part for part in source)

    def test_current_directory_is_original(self):
        self.assertFalse(self.is_error_occurred({
            'decanter': self.assemble('decanter', 'decanter.py'),
            'config': self.assemble('tests', 'decanter', 'config.py')
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble('decanter', 'decanter.py'),
            'config': self.assemble('tests', 'decanter', 'fail_config.py')
        }))

        # '../' in path
        self.assertFalse(self.is_error_occurred({
            'decanter': self.assemble('decanter', '..', 'decanter', 'decanter.py'),
            'config': self.assemble('tests', 'decanter', '..', 'decanter', 'config.py')
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble('decanter', '..', 'decanter', 'decanter.py'),
            'config': self.assemble('tests', '..', 'decanter', 'decanter', 'fail_config.py')
        }))

    def test_current_directory_is_original_and_absolute_path(self):
        self.assertFalse(self.is_error_occurred({
            'decanter': self.assemble(self.dir_of_original, 'decanter', 'decanter.py'),
            'config': self.assemble(self.dir_of_original, 'tests', 'decanter', 'config.py')
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble(self.dir_of_original, 'decanter', 'decanter.py'),
            'config': self.assemble(self.dir_of_original + 'tests', 'decanter', 'fail_config.py')
        }))

    def test_wrong_path(self):
        # wrong path to decanter
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble('wrong', 'path', 'to', 'decanter.py'),
            'config': self.assemble('tests', 'decanter', '..', 'decanter', 'config.py')
        }))
        # wrong path to config
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble('decanter', 'decanter.py'),
            'config': self.assemble('wrong', 'path', 'to', 'config.py')
        }))

    def test_current_directory_is_parent_of_original(self):
        dirname = os.path.basename(self.dir_of_original)
        os.chdir(os.path.dirname(self.dir_of_original))
        self.assertFalse(self.is_error_occurred({
            'decanter': self.assemble(dirname, 'decanter', 'decanter.py'),
            'config': self.assemble(dirname, 'tests', 'decanter', 'config.py')
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble(dirname, 'decanter', 'decanter.py'),
            'config': self.assemble(dirname, 'tests', 'decanter', 'fail_config.py')
        }))

    def test_current_directory_contains_decanterpy(self):
        os.chdir(self.assemble(self.dir_of_original, 'decanter'))
        self.assertFalse(self.is_error_occurred({
            'decanter': 'decanter.py',
            'config': self.assemble('..', 'tests', 'decanter', 'config.py')
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': 'decanter.py',
            'config': self.assemble('..', 'tests', 'decanter', 'fail_config.py')
        }))

    def test_current_directory_contains_config(self):
        os.chdir(self.assemble(self.dir_of_original, 'tests', 'decanter'))
        self.assertFalse(self.is_error_occurred({
            'decanter': self.assemble('..', '..', 'decanter', 'decanter.py'),
            'config': 'config.py'
        }))
        self.assertTrue(self.is_error_occurred({
            'decanter': self.assemble('..', '..', 'decanter', 'decanter.py'),
            'config': 'fail_config.py'
        }))
