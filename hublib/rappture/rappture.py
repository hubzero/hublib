# ----------------------------------------------------------------------
#  COMPONENT: rappture - Python library to read/write Rappture XML
#
# ======================================================================
#  AUTHOR:  Martin Hunt, Purdue University
#  Copyright (c) 2017  HUBzero Foundation, LLC
#
#  See the file "license.terms" for information on usage and
#  redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
# ======================================================================
from __future__ import print_function
from .node import Node
import numpy as np
from lxml import etree as ET
from bs4 import BeautifulSoup


def get_elem_info(elem):
    try:
        id = elem.attrib['id']
    except:
        id = ''
    try:
        label = elem.find("about/label").text
    except:
        label = ''
    try:
        group = elem.find("about/group").text
    except:
        group = ''
    try:
        desc = elem.find("about/description").text
    except:
        desc = ''
    return id, label, group, desc


class RapXML(Node):
    def __init__(self, fname):
        self.fname = fname
        self.tree = ET.parse(fname)
        self.path = ''
        self.copy_defaults()

    def copy_defaults(self):
        # When loading an XML file, check the input section and copy any missing
        # <current> values from their <default>
        for default in self.tree.findall("input//default"):
            current = default.find("../current")
            if current is None:
                par = default.find("..")
                current = ET.SubElement(par, 'current')
                current.text = default.text

    def _repr_html_(self):
        return self.info('all')._repr_html_()

    def __str__(self):
        return self.info('all').__str__()

    def info(self, which='all'):
        d = RapXMLInfo(which)

        if which == 'all' or which == 'inputs':
            inputs = self.tree.find('input')
            if inputs is not None:
                d.append('INPUTS', None)
                self.parse_elem(d, '', inputs)

        if which == 'all' or which == 'outputs':
            outputs = self.tree.find('output')
            if outputs is not None:
                d.append('OUTPUTS', None)
                self.parse_elem(d, '', outputs)

        return d

    def inputs(self):
        return self.info('inputs')

    def outputs(self):
        return self.info('outputs')

    def parse_elem(self, d, path, elem):
        # print("parse:", path, elem.tag)
        if elem.tag == 'number' or \
           elem.tag == 'integer' or \
           elem.tag == 'curve' or \
           elem.tag == 'string' or \
           elem.tag == 'log' or \
           elem.tag == 'boolean' or \
           elem.tag == 'choice' or \
           elem.tag == 'drawing' or \
           elem.tag == 'field' or \
           elem.tag == 'flow' or \
           elem.tag == 'histogram' or \
           elem.tag == 'image' or \
           elem.tag == 'mesh' or \
           elem.tag == 'period element' or \
           elem.tag == 'structure' or \
           elem.tag == 'table':
            d.append(path, elem)
        else:
            if path == '':
                path += elem.tag
            else:
                path += '.%s' % elem.tag
            try:
                path += "(%s)" % elem.attrib['id']
            except:
                pass
            for child in elem:
                self.parse_elem(d, path, child)


class RapXMLInfo(object):

    def __init__(self, which):
        self.elist = []
        self.cgroups = {}

    def append(self, path, elem):
        self.elist.append((path, elem))
        if elem is None:
            return
        if elem.tag == 'curve':
            group = elem.find('about/group')
            if group is not None:
                if group.text in self.cgroups:
                    self.cgroups[group.text].append(elem)
                else:
                    self.cgroups[group.text] = [elem]

    def _repr_html_(self):
        s = ""
        for val in self.elist:
            path, elem = val
            if path == 'INPUTS' or path == 'OUTPUTS':
                if s != "":
                    s += '</table>\n'
                s += '<h3>%s</h3>\n' % path
                s += '<table><tr bgcolor="#cccccc"><th>Path</th><th>Label</th><th>Description</th></tr>\n'
                rnum = 0
                continue
            id, label, group, desc = get_elem_info(elem)
            rnum += 1
            if rnum % 2:
                bg = '#ffffff'
            else:
                bg = '#dddddd'
            s += '<tr bgcolor="%s"><td>%s.%s(%s)</td>' % (bg, path, elem.tag, id)
            s += '<td>%s</td>' % label
            s += '<td>%s</td></tr>' % desc[:40]
        if s != "":
            s += '</table>\n'

        g = ''
        for key in self.cgroups:
            rnum = 0
            if g != "":
                g += '</table>\n'
            g += '<table><tr bgcolor="#cccccc"><th>%s</th>' % key
            for elem in self.cgroups[key]:
                id = elem.attrib['id']
                for path, pelem in self.elist:
                    if pelem is None:
                        continue
                    try:
                        pid = pelem.attrib['id']
                    except:
                        pid = ""
                    if pid == id:
                        rnum += 1
                        if rnum % 2:
                            bg = '#ffffff'
                        else:
                            bg = '#dddddd'
                        g += '<tr bgcolor="%s"><td>%s.%s(%s)</td></tr>\n' % (bg, path, pelem.tag, pid)
                        break
        if g != '':
            g = '<h3>CURVE GROUPS</h3>' + g + '</table>'

        return s + g

    def __str__(self):
        s = ""
        for val in self.elist:
            path, elem = val
            if path == 'INPUTS' or path == 'OUTPUTS':
                if s != "":
                    s += '\n'
                continue
            id, label, group, desc = get_elem_info(elem)
            s += '%s.%s(%s)' % (path, elem.tag, id)
            s += '\t"%s"\n' % label

        g = ''
        for key in self.cgroups:
            rnum = 0
            g += '\n'
            g += 'CURVE GROUP: "%s"' % key
            for elem in self.cgroups[key]:
                id = elem.attrib['id']
                for path, pelem in self.elist:
                    if pelem is None:
                        continue
                    pid = pelem.attrib['id']
                    if pid == id:
                        g += '\n\t%s.%s(%s)' % (path, pelem.tag, pid)
                        break
        return s + g
