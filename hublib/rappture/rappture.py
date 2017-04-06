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
from .util import efind
from glob import glob

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
        if not hasattr(self, 'dirname'):
            self.dirname = None
        self.info = None

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
        self.info = RapXMLInfo(self)
        return self.info._repr_html_()

    def __str__(self):
        self.info = RapXMLInfo(self)
        return str(self.info)

    @property
    def inputs(self):
        self.info = RapXMLInfo(self, 'in')
        return self.info.inputs()

    @property
    def outputs(self):
        self.info = RapXMLInfo(self, 'out')
        return self.info.outputs()



class RapXMLInfo(object):

    def __init__(self, parent, section=''):
        self.ilist = []
        self.olist = []
        self.llist = []
        self.cgroups = {}
        self.parent = parent

        if section == '' or section == 'in':
            inputs = parent.tree.find('input')
            if inputs is not None:
                self.parse_elem('', inputs)

        if section == '' or section == 'out':
            outputs = parent.tree.find('output')
            if outputs is not None:
                self.parse_elem('', outputs)

    def inputs(self):
        return self

    def outputs(self):
        return self

    def append(self, path, elem):
        if path.startswith('input'):
            self.ilist.append((path, elem))
        else:
            self.olist.append((path, elem))

    def parse_loader(self, elem):
        for ex in elem.findall('example'):
            self.llist.append(ex.text)

    def parse_elem(self, path, elem):
        # print("parse:", path, elem.tag)
        if elem.tag == 'number' or \
           elem.tag == 'integer' or \
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
            self.append(path, elem)
        elif  elem.tag == 'curve':
            self.append(path, elem)
            group = elem.find('about/group')
            if group is not None:
                if group.text in self.cgroups:
                    self.cgroups[group.text].append((elem, path))
                else:
                    self.cgroups[group.text] = [(elem, path)]
        elif elem.tag == 'loader':
            self.parse_loader(elem)
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
                self.parse_elem(path, child)

    @staticmethod
    def html_info(info, title):
        s = '<h3>%s</h3>\n' % title
        s += '<table><tr bgcolor="#cccccc"><th>Path</th><th>Label</th><th>Description</th></tr>\n'
        rnum = 0
        for val in info:
            path, elem = val
            pid, label, group, desc = get_elem_info(elem)
            rnum += 1
            if rnum % 2:
                bg = '#ffffff'
            else:
                bg = '#dddddd'
            s += '<tr bgcolor="%s"><td>%s.%s(%s)</td>' % (bg, path, elem.tag, pid)
            s += '<td>%s</td>' % label
            s += '<td>%s</td></tr>' % desc[:40]
        s += '</table>\n'
        return s

    @staticmethod
    def str_info(info, title):
        s = '%s\n' % title
        for val in info:
            path, elem = val
            pid, label, group, desc = get_elem_info(elem)
            s += '%s.%s(%s)\t%s\n\t%s' % (path, elem.tag, pid, label, desc[:60])
        return s

    @staticmethod
    def loader_html(llist, dirname):
        s = "<h3>Loaders</h3><table>"
        for val in llist:
            rnum = 0
            if dirname is None:
                if rnum % 2:
                    bg = '#ffffff'
                else:
                    bg = '#dddddd'
                s += '<tr bgcolor="%s"><td>%s</td></tr>' % (bg, val)
                rnum += 1
            else:
                path = '%s/rappture/examples/%s' % (dirname, val)
                for file in glob(path):
                    if rnum % 2:
                        bg = '#ffffff'
                    else:
                        bg = '#dddddd'
                    s += '<tr bgcolor="%s"><td>%s</td></tr>' % (bg, file)
                    rnum += 1
        s += '</table>'
        return s

    @staticmethod
    def html_groups(groups):
        table = '<h3>CURVE GROUPS</h3>\n'
        for key in groups:
            rnum = 0
            g = '<table><tr bgcolor="#cccccc"><th>%s</th>\n' % key
            for elem, path in groups[key]:
                rnum += 1
                if rnum % 2:
                    bg = '#ffffff'
                else:
                    bg = '#dddddd'
                pid = elem.attrib['id']
                g += '<tr bgcolor="%s"><td>%s.%s(%s)</td></tr>\n' % (bg, path, elem.tag, pid)
            table += g + '</table>'
        return table

    @staticmethod
    def str_groups(groups):
        g = "\nCurve Groups"
        for key in groups:
            g += '\n%s\n' % key
            for elem, path in groups[key]:
                pid = elem.attrib['id']
                g += '\t%s.%s(%s)\n' % (path, elem.tag, pid)
        return g

    def _repr_html_(self):
        outstr = ""
        if self.ilist:
            outstr += RapXMLInfo.html_info(self.ilist, 'INPUTS')
            if self.llist:
                outstr += RapXMLInfo.loader_html(self.llist, self.parent.dirname)

        if self.olist:
            outstr += RapXMLInfo.html_info(self.olist, 'OUTPUTS')
            if self.cgroups:
                outstr += RapXMLInfo.html_groups(self.cgroups)
        return outstr

    def __str__(self):
        outstr = ""
        if self.ilist:
            outstr += RapXMLInfo.str_info(self.ilist, 'INPUTS')

        if self.olist:
            if outstr != "":
                outstr += '\n'
            outstr += RapXMLInfo.str_info(self.olist, 'OUTPUTS')
            if self.cgroups:
                outstr += RapXMLInfo.str_groups(self.cgroups)

        return outstr

