#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import sys

enum = 0
num = 0

while num < 2000:
    if num % 10 == 0:
        print("STDERR %s" % enum, file=sys.stderr)
        sys.stderr.flush()
        enum += 1
    print("%03d : Ńobody expects the Spanish Inquisition!" % num)
    sys.stdout.flush()
    num += 1
    time.sleep(.1)
