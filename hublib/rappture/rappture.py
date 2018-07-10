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
import os
import pandas as pd
import qgrid
from IPython.display import Markdown
from .node import Node
from lxml import etree as ET
from glob import glob
from .loader import RapLoader
#qgrid.enable()


def get_elem_info(elem):
    try:
        id = elem.attrib['id']
    except:
        id = ''
    try:
        label = elem.find("about/label").text
    except:
        label = None
    try:
        group = elem.find("about/group").text
    except:
        group = None
    try:
        desc = elem.find("about/description").text
    except:
        desc = None
    if desc is None:
        desc = ''
    if label is None:
        label = ''
    if group is None:
        group = ''
    return id, label, group, desc


class RapXML(Node):

    def __init__(self, fname):
        self.fname = fname
        parser = ET.XMLParser(remove_comments=True)
        self.tree = ET.parse(fname, parser)
        self.path = ''
        if hasattr(self, 'dirname'):
            # only Tools have dirname
            RapLoader.copy_defaults(self.tree, reset=True)
            self._load_loaders()
        else:
            try:
                self.dirname = self.tree.find('tool/version/application/directory[@id]').text
                self.dirname = os.path.split(self.dirname)[0]
            except:
                self.dirname = None
        self.top = self
        self.info = RapXMLInfo(self)
        
    def reload(self):
        self.info = RapXMLInfo(self)

    def _load_loaders(self):
        # now load all the default loaders
        for loader in self.tree.findall("input//loader"):
            # print("Found loader", loader)
            default = loader.find("default")
            current = loader.find("current")
            if current is None:
                current = ET.SubElement(loader, 'current')

            for ex in loader.findall('example'):
                path = os.path.join(self.dirname, "rappture", "examples", ex.text)
                # print("path=", path)
                for file in glob(path):
                    if os.path.basename(file) == default.text:
                        RapLoader.load(self.tree, loader, current, file)
                        break
    
    def set_input(self, label, val):
        match = self.info.in_df[self.info.in_df['Label'] == label].index.tolist()
        if len(match) == 0:
            # maybe a loader?
            match = self.info.loader_df[self.info.loader_df['Label'] == label].index.tolist()
            if len(match) > 0:
                match = [match[0]]
        if len(match) == 0:
            raise ValueError("No matches with that label.")
        if len(match) > 1:
            raise ValueError("Error: %d labels match." % len(match))
        self[match[0]] = val

    def get_input(self, label):
        match = self.info.in_df[self.info.in_df['Label'] == label].index.tolist()
        if len(match) == 0:
            # maybe a loader?
            match = self.info.loader_df[self.info.loader_df['Label'] == label].index.tolist()
            if len(match) > 0:
                match = [match[0]]
        if len(match) == 0:            
            raise ValueError("No matches with that label.")
        if len(match) > 1:
            raise ValueError("Error: %d labels match." % len(match))
        return self[match[0]]

    def set_output(self, label, val):
        match = self.info.out_df[self.info.out_df['Label'] == label].index.tolist()
        if len(match) == 0:
            raise ValueError("No matches with that label.")
        if len(match) > 1:
            raise ValueError("Error: %d labels match." % len(match))
        self[match[0]] = val

    def get_output(self, label):
        match = self.info.out_df[self.info.out_df['Label'] == label].index.tolist()
        if len(match) == 0:            
            raise ValueError("No matches with that label.")
        if len(match) > 1:
            raise ValueError("Error: %d labels match." % len(match))
        return self[match[0]]

    def create_input_widget(self, label):
        match = self.info.in_df[self.info.in_df['Label'] == label].index.tolist()
        if len(match) == 0:
            raise ValueError("No matches with that label.")
        if len(match) > 1:
            raise ValueError("Error: %d labels match." % len(match))
        return self[match[0]].w


    def _ipython_display_(self):
        if self.info.in_df.size:
            display(Markdown('## INPUTS'), qgrid.show_grid(self.info.in_df, grid_options={'editable': False}))
        if self.info.loader_df.size:
            display(Markdown('## LOADERS'), qgrid.show_grid(self.info.loader_df, grid_options={'editable': False}))
        if self.info.out_df.size:
            display(Markdown('## OUTPUTS'), qgrid.show_grid(self.info.out_df, grid_options={'editable': False}))

    @property
    def inputs(self):
        display(Markdown('## INPUTS'), qgrid.show_grid(self.info.in_df, grid_options={'editable': False}))
        if self.info.loader_df.size:
            display(Markdown('## LOADERS'), qgrid.show_grid(self.info.loader_df, grid_options={'editable': False}))

    @property
    def outputs(self):
        display(qgrid.show_grid(self.info.out_df, grid_options={'editable': False}))        


    @property
    def loaders(self):
        display(qgrid.show_grid(self.info.loader_df, grid_options={'editable': False}))


class RapXMLInfo(object):

    def __init__(self, parent):

        self.ilist = {'Path':[], 'Label':[], 'Description':[]}
        self.olist = {'Path':[], 'Label':[], 'Group':[], 'Description':[]}
        self.llist = {'Path':[], 'Label':[], 'Description':[],
                      'File':[], 'FileLabel':[], 'FileDescription':[]}
        self.parent = parent

        inputs = parent.tree.find('input')
        if inputs is not None:
            self.parse_elem('', inputs)

        outputs = parent.tree.find('output')
        if outputs is not None:
            self.parse_elem('', outputs)

        # save all data in dataframes
        self.in_df = pd.DataFrame(data=self.ilist, columns=['Path', 'Label', 'Description'])
        self.in_df = self.in_df.set_index('Path')
        self.out_df = pd.DataFrame(data=self.olist, columns=['Path', 'Label', 'Group', 'Description'])
        self.out_df = self.out_df.set_index('Path')
        self.loader_df = pd.DataFrame(data=self.llist, columns=['Path', 'Label', 'Description',
                                                                'File', 'FileLabel', 'FileDescription'])
        self.loader_df = self.loader_df.set_index('Path')

    def append(self, path, elem):
        pid, label, group, desc = get_elem_info(elem)
        if pid:
            path = '%s.%s(%s)' % (path, elem.tag, pid)
        else:
            path = '%s.%s' % (path, elem.tag)

        if path.startswith('input'):
            self.ilist['Path'].append(path)
            self.ilist['Label'].append(label)
            self.ilist['Description'].append(desc)
        else:
            self.olist['Path'].append(path)
            self.olist['Label'].append(label)
            self.olist['Group'].append(group)
            self.olist['Description'].append(desc)

    def parse_loader(self, elem, path):
        tdir = self.parent.dirname
        try:
            label = elem.find('about/label').text
            try:
                desc = elem.find('about/description').text
            except:
                desc = ''
            path += '.loader'
            try:
                _id = elem.attrib['id']
                path = path + '(%s)' % _id
            except:
                pass
            # print("LOADER: label=%s path=%s desc=%s" % (label, path, desc))
            for ex in elem.findall('example'):
                # print('ex=', ex.text)
                fpath = '%s/rappture/examples/%s' % (tdir, ex.text)
                for file in glob(fpath):
                    if file.endswith('.'):
                        continue
                    r = ET.parse(file).getroot()
                    flabel = r.find('about/label').text
                    try:
                        fdesc = r.find('about/description').text
                    except:
                        fdesc = ''
                    # print(file, flabel, fdesc)
                    self.llist['Path'].append(path)
                    self.llist['Label'].append(label)
                    self.llist['Description'].append(desc)
                    self.llist['File'].append(file)
                    self.llist['FileLabel'].append(flabel)
                    self.llist['FileDescription'].append(fdesc)
        except:
            pass


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
           elem.tag == 'curve' or \
           elem.tag == 'table':
            self.append(path, elem)
        elif elem.tag == 'loader':
            self.parse_loader(elem, path)
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
