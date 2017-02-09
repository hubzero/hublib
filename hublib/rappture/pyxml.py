# ----------------------------------------------------------------------
#  COMPONENT: PyXml - Python access to the Rappture XML library
#
# ======================================================================
#  AUTHOR:  Martin Hunt, Purdue University
#  Copyright (c) 2015  HUBzero Foundation, LLC
#
#  See the file "license.terms" for information on usage and
#  redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
# ======================================================================
from library import library
from result import result
import numpy as np

"""
This library provides a simpler way to read and write Rappture
XML for Python tools.  It is backwards-compatible with the old
library API.

See python_api.rst for docs.
"""


def PyXml(path):
    '''
    Open the Rappture xml file located at 'path' and return a node
    reference to the root.
    '''
    lib = library(path)
    return Node(lib, '')


class Node:
    def __init__(self, library, path):
        self.lib = library
        self.path = path

    def __setitem__(self, path, val):
        self.put(path, val)

    def __getitem__(self, path):
        if self.path != '':
            path = self.path + '.' + path
        return Node(self.lib, path)

    def get(self, path):
        return self.__getitem__(path).value

    def put(self, path, val, **kwargs):
        if self.path != '':
            path = self.path + '.' + path

        if type(val) == np.ndarray:
            val = ' '.join(map(str, val.ravel('F').tolist()))
        elif type(val) == list or type(val) == tuple:
            val = '\n'.join([' '.join(map(repr, x)) for x in zip(*val)])
            # we need the strings double quoted for tcl
            val = val.replace("'", '"')
        self.lib.put(path, val, **kwargs)

    @property
    def value(self):
        return self.lib.get(self.path)

    @property
    def name(self):
        return self.path

    def __str__(self):
        if self.path != '':
            return("%s['%s']" % (self.lib, self.path))
        return str(self.lib)

    def copy(self, dest, src):
        return self.lib.copy(dest, src)

    def xml(self):
        elem = self.lib.element(self.path)
        return elem.xml()

    def close(self, status=0):
        self.lib.result(status)
        result(self.lib)

