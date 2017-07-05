#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys, os
sys.path.insert(0, os.path.abspath('../../..'))
from hublib.cmd import executeCommand, runCommand, get_stdin

a = 'foo.py'
print(get_stdin(a))
a = u'foo.py'
print(get_stdin(a))

a = 'ಕನ್ನಡ.txt'
print(get_stdin(a))
a = u'ಕನ್ನಡ.txt'
print(get_stdin(a))

a = open('ಕನ್ನಡ.txt')
print(get_stdin(a))

a = open('foo.py')
print(get_stdin(a))

a = open('ಕನ್ನಡ.txt')
print(get_stdin(a.fileno()))

a = open('foo.py')
print(get_stdin(a.fileno()))

a = 'no_such_file'
print(get_stdin(a))

print(get_stdin(3.14159))

out = runCommand('ls', stream=False)[1]
print("out=%s" % out)

"""
code, out, err = runCommand('top')
print("code=%s" % code)
print("out=%s" % out)
print("err=%s" % err)
"""

code, out, err = executeCommand(u'./UnicodeTestλ.py', stdin='ಕನ್ನಡ.txt', streamOutput=True)
print(code)
# print(out.decode('utf-8'))

print('\n\n\n')
code, out, err = runCommand('cat ಕನ್ನಡ.txt')
out = out.decode('utf-8')
print(out)
