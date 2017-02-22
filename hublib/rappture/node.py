from __future__ import print_function
from lxml import etree as ET
import numpy as np
from bs4 import BeautifulSoup

from io import BytesIO
import pint
from .. import ureg, Q_
from base64 import b64decode, b64encode
import zlib
import imghdr
from IPython.display import HTML
from .image import RapImage, encode
from .curve import curve_plot, mcurve_plot
from .structure import structure_plot
from .hist import hist_plot


def _to_xpath(path):
    xpath = []
    for a in path.split('.'):
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


def parse_py_num(val, uelem):
    # units are rappture units
    # val is a python string, for example, "100 C", or "100"
    # OR a number OR a PINT expression

    vunits = ''
    if hasattr(val, 'units'):
        vunits = val.units

    if vunits == '':
        # Not PINT, so just set to string value
        return str(val)

    if uelem is None or uelem.text == '':
        # Rappture doesn't want units, but our expression has them!!!!
        raise ValueError("This Rappture element does not have Units!!")

    # Rappture wants units and we have them

    # convert Rappture units to PINT units
    if uelem.text == 'C':
        units = ureg.degC
    else:
        units = ureg.parse_expression(uelem.text).units

    # let PINT do the conversion
    val = val.to(units)

    # return a Rappture-friendly string
    return '%s %s' % (val.magnitude, uelem.text)


def parse_rap_expr(units, val):
    # units and val are strings from rappture
    # We need to convert them to PINT expressions
    # print("PARSE:", units, val)
    if units is None or units == '':
        return val

    # Rappture compatibility. C is Celsius, not Coulombs
    if units == 'C':
        units = ureg.degC
    else :
        units = ureg.parse_expression(units).units

    try:
        val = ureg.parse_expression(val)
        if hasattr(val, 'units'):
            if val.units == ureg.coulomb and (units == ureg.K or units == ureg.degC):
                # C -> Celsius
                val = Q_(val.magnitude, ureg.degC)
            val = val.to(units)
        else:
            val = Q_(val, units)
        return val
    except:
        raise ValueError("Bad input value.")


# convert XML values to python values
def _convert(elem, val, magnitude=False, units=False):
    tag = elem.tag
    # print("CONVERT", tag, val)

    if tag == 'integer':
        return int(val)

    if tag == 'boolean':
        if val in ['true', '1', 'yes', 'on', 1]:
            return True
        else:
            return False

    if tag == 'number':
        u = elem.find('units')
        if units:
            if u is None or u.text == '':
                return ''
            return ureg.parse_expression(u.text).units
        if u is None or u == '':
            return float(val)

        val = parse_rap_expr(u.text, val)
        if magnitude:
            return val.magnitude
        return val

    if tag == 'xy':
        return np.fromstring(val, sep=' \n').reshape(-1, 2)

    if tag == 'image':
        return RapImage(val)

    return val


# format python values for writing to Rappture XML
def _format(elem, val):
    tag = elem.tag
    # print("FORMAT", tag, val)

    if tag == 'number':
        u = elem.find('units')
        return parse_py_num(val, u)

    if tag == 'boolean':
        if val in [True, 1, '1', 'true', 'True', 'yes', 'Yes', 'On', 'on']:
            return 'true'
        return 'false'

    if tag == 'image':
        return encode(val)

    if tag == 'xy':
        if type(val) == np.ndarray:
            s = BytesIO()
            np.savetxt(s, val, fmt='%.6e %.6e', newline="\n")
            return s.getvalue()
        elif type(val) == list or type(val) == tuple:
            val = '\n'.join([' '.join(map(repr, x)) for x in zip(*val)])
            # we need the strings double quoted for tcl
            return val.replace("'", '"')

    return str(val)


class Node(object):
    def __init__(self, tree, path):
        self.tree = tree
        self.path = path

    def __setitem__(self, path, val):
        if self.path != '':
            path = self.path + '.' + path

        # print("PUT: path=", path)
        x = _create_path(self.tree.getroot(), path)
        if x is None:
            return False
        # print("PUT:", x, x.tag)

        if x.tag == 'current' or x.tag == 'default':
            elem = x.find('..')
            # print("x=%s elem=%s" % (x, elem))
        else:
            # If there is a 'current' child, set that.
            elem = x
            x = elem.find('current')
            if x is None:
                x = elem
        # print("setting %s to %s" % (elem, val))
        x.text = _format(elem, val)
        return True

    def __getitem__(self, path):
        if self.path != '':
            path = self.path + '.' + path
        return Node(self.tree, path)

    def _value(self, magnitude=False, units=False):
        xpath = _to_xpath(self.path)
        x = self.tree.find(xpath)
        if x is None:
            return None
        if x.tag == 'current' or x.tag == 'default':
            elem = x.find('..')
            val = x.text
        else:
            elem = x
            current = x.find('current')
            if current is None:
                val = x.text
            else:
                val = current.text
        return _convert(elem, val, magnitude, units)

    @property
    def value(self):
        return self._value()

    @property
    def magnitude(self):
        return self._value(magnitude=True)

    @property
    def units(self):
        return self._value(units=True)

    @property
    def rvalue(self):
        xpath = _to_xpath(self.path)
        x = self.tree.find(xpath)
        if x is None:
            return None
        if x.tag == 'current' or x.tag == 'default':
            val = x.text
        else:
            tag = x.tag
            current = x.find('current')
            if current is None:
                val = x.text
            else:
                val = current.text
        return val

    @property
    def name(self):
        return self.path

    def plot(self, single=False, **kwargs):
        """
        Plots a curve, curve group, structure(molecule), or histogram.

        :param single: Plot just a single curve instead of an entire group.
        """
        xpath = _to_xpath(self.path)
        elem = self.tree.find(xpath)

        if elem.tag == 'curve':
            if single is False and elem.find("about/group") is not None:
                return mcurve_plot(elem)
            return curve_plot(elem, **kwargs)

        if elem.tag == 'structure':
            return structure_plot(elem, **kwargs)

        if elem.tag == 'histogram':
            return hist_plot(elem, **kwargs)

        return

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
            xml = '<?xml version="1.0"?>\n' + xml
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
