from __future__ import print_function
from lxml import etree as ET
import numpy as np
import pint
from .. import ureg, Q_

import os
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display
import tempfile
import nglview as nv
from .util import efind
from .node import Node


class Structure(Node):

    def plot(self):
        """
        Display a rappture structure
        """

        elem = self.elem

        # if there is a 'current' element, display that
        current = elem.find('current')
        if current:
            elem = current

        for child in elem:
            if child.tag == 'about':
                label = efind(child, 'label')
                continue
            if child.tag == 'units':
                units = child.text
                continue
            if child.tag == 'updir':
                updir = child.text
                continue
            if child.tag != 'components':
                print("ERROR: '%s' in struct not component" % child.tag)
                return
            self.component_plot(child, label)

    def component_plot(self, elem, label):
        for child in elem:
            if child.tag == 'molecule':
                return self.molecule_plot(child, label)
            print("Component '%s' not implemented yet." % child.tag)

    def molecule_plot(self, elem, label):
        " Read in a list of atoms and write a PDB file for nglview."
        formula = efind(elem, 'formula')
        if formula == 'pdt' or formula == 'tube' or formula == 'cell':
            f = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdb')
            for child in elem:
                if child.tag == 'atom':
                    id = int(child.attrib['id'])
                    symbol = efind(child, 'symbol')
                    xyz = efind(child, 'xyz')
                    x, y, z = [float(x) for x in xyz.split()]
                    print("ATOM  {:5d} {:>2}           1    {:8.3f}{:8.3f}{:8.3f} ".format(id, symbol, x, y, z), file=f)
            f.close()

        pdb = efind(elem, 'pdb')
        if pdb:
            f = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdb')
            print(pdb, file=f)
            f.close()
            
        w = nv.show_structure_file(f.name)
        w.representations = [
            {"type": "ball+stick", "params": {}}
        ]
        w.parameters = {
            "backgroundColor": "black",
        }
        os.unlink(f.name)
        display(w)
