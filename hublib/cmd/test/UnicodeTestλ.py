#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys


while True:
    a = sys.stdin.readline()
    if a == '':
        break
    sys.stdout.write(a)

print('\n')
print('👍' * 10)
