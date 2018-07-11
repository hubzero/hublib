from __future__ import print_function
from lxml import etree as ET
import numpy as np
from bs4 import BeautifulSoup


import pint
from .. import ureg, Q_
from base64 import b64decode, b64encode
import zlib
import imghdr
from IPython.display import HTML


"""
foo = node[path]
    Looks up path from node and returns a Node.

foo = node[path].value
    Looks up path from node and creates a Node. calls Node.value()

node[path].display(..)
    Looks up path from node and creates a Node. calls Node.display()

node[path] = val
    Looks up path from node and creates a Node. Creates path if necessary.
    Calls Node._setval()

node[path].value = val
    Same as previous.

node[path].rvalue = val
    Looks up path from node and creates a Node. Sets the node text to val (a string)

Dealing with current and default. When looking up a node and its
tag is 'current' or 'default', the parent Node is returned with self.child
set to the 'current' or 'default' element.


"""


# parse a rappture path and return a list
def _parse_rappath(path):
    a = ""
    res = []
    paren = False
    for s in path:
        if s == '.' and paren is False:
            res.append(a)
            a = ""
        else:
            a += s
            if s == '(':
                paren = True
            elif s == ')':
                paren = False
    res.append(a)
    return res


def _to_xpath(path):
    xpath = []
    for a in _parse_rappath(path):
        par = a.find('(')
        if par > -1:
            id = a[par+1:-1]
            elem = a[:par]
            xpath.append('%s[@id=\"%s"]' % (elem, id))
        else:
            xpath.append(a)
    return '/'.join(xpath)


def _create_path(root, path):
    for a in path.split('.'):
        # print('root=', root)
        par = a.find('(')
        # print("par=", par)
        if par > -1:
            id = a[par+1:-1]
            elem = a[:par]
            xpath = '%s[@id=\"%s"]' % (elem, id)
        else:
            id = None
            elem = a
            xpath = a
        # print("root=%s xpath=%s  elem=%s" % (root, xpath, elem))
        nt = root.find(xpath)
        if nt is None:
            if id is None:
                # print("creating %s.%s" %(root, elem))
                root = ET.SubElement(root, elem)
            else:
                # print("Creating %s.%s(%s)" %(root, elem, id))
                root = ET.SubElement(root, elem, attrib={'id': id})
        else:
            root = nt
    return root


class Node(object):
    def __init__(self, top, tree, path, elem=None, child=None):
        self.top = top
        self.tree = tree
        self.path = path
        self.elem = elem
        self.child = child

    def create(self, path='', create=False):
        # print("Create", self.path, path)
        if self.path != '':
            if path != '':
                path = self.path + '.' + path
            else:
                path = self.path

        # print("create", path)
        # find the xml element from a node path
        xpath = _to_xpath(path)
        if create:
            x = _create_path(self.tree.getroot(), path)
        else:
            x = self.tree.find(xpath)

        if x is None:
            return None

        if x.tag == 'current' or x.tag == 'default':
            child = x
            x = child.find('..')
        else:
            child = x.find('current')

        # Create an object corresponding to the tag.
        if x.tag == 'curve':
            return Curve(self.top, self.tree, path, x, child)
        if x.tag == 'number':
            return Number(self.top, self.tree, path, x, child)
        if x.tag == 'integer':
            return RapInt(self.top, self.tree, path, x, child)
        if x.tag == 'boolean':
            return RapBool(self.top, self.tree, path, x, child)
        if x.tag == 'structure':
            return Structure(self.top, self.tree, path, x, child)
        if x.tag == 'histogram':
            return Histogram(self.top, self.tree, path, x, child)
        if x.tag == 'image':
            return RapImage(self.top, self.tree, path, x, child)
        if x.tag == 'xy':
            return XY(self.top, self.tree, path, x, child)
        if x.tag == 'min' or x.tag == 'max':
            return RapMinMax(self.top, self.tree, path, x, child)
        if x.tag == 'log':
            return RapLog(self.top, self.tree, path, x, child)
        if x.tag == 'loader':
            return RapLoader(self.top, self.tree, path, x, child)
        return Node(self.top, self.tree, path, x, child)

    def __setitem__(self, path, val):
        # print("SETITEM ", self.tree, self.path, path, val)
        n = self.create(path, create=True)
        if n is None:
            return False
        n.value = val
        self.top.reload()
        return True

    def __getitem__(self, path):
        # print("GETITEM ", self.tree, self.path, path)
        return self.create(path)

    # Why do we need this? Because elem.text will not see the text that
    # is after child nodes, for example
    # <log><about><label>TEXT</label></about> Here is my log file info... </log>
    # Probably only need for log messages
    def all_text(self):
        s = []
        if self.elem.text:
            s.append(self.elem.text)
        for child in self.elem.getchildren():
            if child.tail:
                s.append(child.tail)
        return ''.join(s).strip()

    # get text from a Node or its child(current or default) if present
    def get_text(self):
        if self.child is not None:
            return self.child.text
        return self.elem.text

    # set text in a Node or its child(current or default) if present
    def set_text(self, val):
        if self.child is not None:
            self.child.text = val
        else:
            self.elem.text = val

    @property
    def value(self):
        return self.rvalue

    @value.setter
    def value(self, val):
        self.set_text(str(val))

    @property
    def rvalue(self):
        return self.get_text()

    @rvalue.setter
    def rvalue(self, val):
        self.set_text(val)

    @property
    def name(self):
        return self.path

    def __str__(self):
        return("%s['%s']" % (self.tree, self.path))

    """
    # ipython pretty print method
    def _repr_pretty_(self, p, cycle):
        if cycle:
            return
        p.text(self.__str__())
    """

    def xml(self, pretty=True, header=False):
        if self.path == '':
            elem = self.tree.getroot()
        else:
            xpath = _to_xpath(self.path)
            elem = self.tree.find(xpath)
        xml = ET.tostring(elem, pretty_print=pretty)
        if header is True:
            xml = b'<?xml version="1.0"?>\n' + xml
        return XMLOut(xml)


class XMLOut(object):
    def __init__(self, xml):
        self.xml = xml

    def _repr_pretty_(self, p, cycle):
        if cycle:
            return
        p.text(self.__str__())

    def __str__(self):
        return self.xml.decode("utf-8")


from .curve import Curve
from .structure import Structure
from .hist import Histogram
from .image import RapImage
from .number import Number
from .integer import RapInt, RapBool, XY, RapMinMax, RapLog
from .loader import RapLoader
