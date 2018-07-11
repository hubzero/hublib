from __future__ import print_function
from .. import ureg, Q_
from io import BytesIO
import numpy as np
from .node import Node
from .number import parse_rap_expr
from .util import from_rap
from .. import ui as ui


class RapInt(Node):

    @property
    def w(self):
        vals = from_rap(self)
        w = ui.Integer(
            name=vals['label'],
            desc=vals['desc'],
            units=vals['units'],
            min=vals['min'],
            max=vals['max'],
            value=vals['value'],
            cb=lambda x, y: RapInt.value.fset(self, w.value)
        )
        return w

    @property
    def value(self):
        return int(self.get_text())

    @value.setter
    def value(self, val):
        self.set_text(str(val))


class RapMinMax(Node):
    def text_to_number(self, par):
        val = self.get_text()
        u = par.find('units')
        if u is None or u == '' or (type(u) == str and u.startswith('/')):
            return float(val)
        val = parse_rap_expr(u.text, val)
        if type(val) == str:
            return val
        return val.magnitude

    @property
    def value(self):
        par = self.elem.find('..')
        if par.tag == 'integer':
            return int(self.get_text())
        return float(self.text_to_number(par))

    @value.setter
    def value(self, val):
        self.set_text(str(val))


class RapBool(Node):
    @property
    def value(self):
        if self.get_text() in ['true', '1', 'yes', 'on', 1]:
            return True
        else:
            return False

    @value.setter
    def value(self, val):
        if val in [True, 1, '1', 'true', 'True', 'yes', 'Yes', 'On', 'on']:
            self.set_text('true')
        else:
            self.set_text('false')


class XY(Node):
    """
    xy can be a name/value pairs for a histogram or x,y pairs for a curve
    """
    @property
    def value(self):
        try:
            par = self.elem.find('../..')
        except:
            ValueError("Could not find xy parents.")

        val = self.elem.text
        if par.tag == 'curve':
            # return a 2D numpy array
            res = np.fromstring(val, sep=' \n').reshape(-1, 2)
        else:
            # return a list of (name, value) tuples
            it = iter(shlex.split(val))
            res = zip(it, it)
        return res

    @value.setter
    def value(self, val):
        if type(val) == np.ndarray:
            s = BytesIO()
            np.savetxt(s, val, fmt='%.6e %.6e', newline="\n")
            res = s.getvalue()
        elif type(val) == list or type(val) == tuple:
            val = '\n'.join([' '.join(map(repr, x)) for x in zip(*val)])
            # we need the strings double quoted for tcl
            res = val.replace("'", '"')
        self.elem.text = res


class RapLog(Node):
    @property
    def value(self):
        return self.all_text()

    @value.setter
    def value(self, val):
        self.set_text(str(val))
