#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import imp
import os


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for root, dirs, files in os.walk('tests'):
        for f in files:
            if f == 'tests.py':
                current_path = os.path.join(root, f)
                mod = imp.load_source(os.path.splitext(current_path)[0], current_path)
                suite.addTest(loader.loadTestsFromModule(mod))

    unittest.TextTestRunner(verbosity=1).run(suite)
