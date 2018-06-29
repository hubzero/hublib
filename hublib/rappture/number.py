from __future__ import print_function
from .. import ureg, Q_
from .node import Node
from .. import ui as ui
from .util import from_rap


def parse_rap_expr(units, val):
    # units and val are strings from rappture
    # We need to convert them to PINT expressions
    # print("PARSE:", units, val)
    if units is None or units == '':
        return val

    # Rappture compatibility. C is Celsius, not Coulombs
    if units == 'C':
        units = ureg.degC
    else:
        try:
            units = ureg.parse_expression(units).units
        except:
            pass

    # Another Rappture compatibility hack
    if type(units) == str and units.startswith('/'):
        try:
            ind = val.index(units)
            return val[0:ind]
        except:
            return val
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


class Number(Node):

    @property
    def w(self):
        vals = from_rap(self)
        w = ui.Number(
            name=vals['label'],
            desc=vals['label'],
            units=vals['units'],
            min=vals['min'],
            max=vals['max'],
            value=vals['value'],
            cb=lambda x, y: Number.value.fset(self, w.value)
        )
        return w

    def text_to_number(self, magnitude=False, units=False):
        val = self.get_text()
        u = self.elem.find('units')
        # print("val=%s, units=%s u=%s" % (val, units, u.text))
        if units:
            if u is None or u.text == '':
                return ''
            return ureg.parse_expression(u.text).units
        if u is None or u == '' or (type(u) == str and u.startswith('/')):
            return float(val)

        val = parse_rap_expr(u.text, val)
        if type(val) == str:
            return float(val)

        if magnitude:
            return val.magnitude
        return val

    @property
    def value(self):
        # return self.text_to_number()
        return self.text_to_number(magnitude=True)

    @value.setter
    def value(self, val):
        # print("SET NUMBER VALUE to", val)

        vunits = ''
        if hasattr(val, 'units'):
            vunits = val.units

        if vunits == '':
            # Not PINT, so just set to string value
            self.set_text(str(val))
            return

        uelem = self.elem.find('units')
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

        # a Rappture-friendly string
        self.set_text('%s %s' % (val.magnitude, uelem.text))

    @property
    def magnitude(self):
        # same as value
        return self.text_to_number(magnitude=True)

    @property
    def units(self):
        return self.text_to_number(units=True)