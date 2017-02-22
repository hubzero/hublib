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


def efind(elem, path):
    try:
        text = elem.find(path).text
    except:
        text = ""
    return text


def structure_plot(elem):
    """
    Display a rappture structure
    """

    # if there is a 'current' element, display that
    current = elem.find('current')
    if current:
        elem = current

    for child in elem:
        if child.tag == 'about':
            label = efind(child, 'label')
            continue
        if child.tag != 'components':
            print("ERROR: '%s' in struct not component" % child.tag)
            return
        component_plot(child, label)


def component_plot(elem, label):
    for child in elem:
        if child.tag == 'molecule':
            return molecule_plot(child, label)
        print("Component '%s' not implemented yet." % child.tag)


def molecule_plot(elem, label):
    " Read in a list of atoms and write a PDB file for nglview."
    formula = efind(elem, 'formula')
    f = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdb')

    for child in elem:
        if child.tag == 'atom':
            id = int(child.attrib['id'])
            symbol = efind(child, 'symbol')
            xyz = efind(child, 'xyz')
            x, y, z = [float(x) for x in xyz.split()]
            print("ATOM  {:5d} {:>2}           1    {:8.3f}{:8.3f}{:8.3f} ".format(id, symbol, x, y, z), file=f)
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
