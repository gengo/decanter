#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
import decanter

if __name__ == '__main__':
    decanter.parse_args()

