import ipywidgets as widgets
from IPython.display import display, HTML
import pint


ureg = pint.UnitRegistry()
ureg.autoconvert_offset_to_baseunit = True


def find_unit(xpr):
    if hasattr(xpr, 'compatible_units'):
        return xpr
    return ureg.parse_expression(xpr).units


class NumValue(object):

    def __init__(self, name, desc, **kwargs):

        label_layout = widgets.Layout(flex='1 1 auto')

        width = kwargs.get('width', 'auto')

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )

        cb = kwargs.get('cb')

        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.default = self.dd.value

        self.units = kwargs.get('units')
        if self.units is not None:
            self.units = find_unit(self.units)
            desc += "\n\nValues with no units will be assumed to be %s [%s]." % (self.units, '{:~}'.format(self.units))

        if self.min is not None or self.max is not None:
            desc += "\n\n"
            if self.min is not None:
                desc += "Min: %s\n" % self.min
            if self.max is not None:
                desc += "Max: %s\n" % self.max
            desc += "\n"

        if self.units:
            desc += "You can type expressions using other units and they will be converted if possible."

        self.label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.valid = widgets.Valid(value=True, layout=widgets.Layout(flex='0 1 auto'))
        self.w = widgets.Box([self.label, self.dd, self.valid], layout=form_item_layout)
        try:
            self.dd.on_submit(lambda x: self.cb(None))
        except:
            pass
        self.dd.observe(lambda x: self.cb(x['new']), names='value')

        self._cb = cb
        self.name = name
        self.oldval = None
        self.no_cb = False

        if self.min is not None:
            self.min = self.type(self.parse_expr(self.min, True))
        if self.max is not None:
            self.max = self.type(self.parse_expr(self.max, True))


    def parse_expr(self, val, magnitude=False):
        print "parse_expr", str(val), self.units
        if val is None:
            return val

        try:
            val = ureg.parse_expression(str(val))
            if self.units is None:
                if hasattr(val, 'units'):
                    raise ValueError("No units were expected")
                return str(val)
            if hasattr(val, 'units'):
                val = val.to(self.units)
            else:
                val *= self.units
            if magnitude:
                return val.magnitude
            return val
        except:
            raise ValueError("Bad input value.")


    def check(self, val):
        # Does range checking
        print "check", val, self.units, self.type
        if val is None:
            return False

        if self.units:
            mag = self.type(val.magnitude)
        else:
            print("VAL:", val, type(val))
            mag = self.type(val)

        if self.max is not None and mag > self.max:
            return False
        if self.min is not None and mag < self.min:
            return False
        return True


    def cb(self, _):
        '''
        Called when the value changed.  It is called after every keystroke, so
        we check on the fly and only reformat on <enter> or when the value property is read.
        '''
        print "cb val=%s oldval=%s no_cb=%s" % (self.dd.value, self.oldval, self.no_cb)
        if self.no_cb:
            self.no_cb = False
            return

        val = self.parse_expr(self.dd.value)

        if self.oldval == self.dd.value:
            # The value did not change; the user hit enter.
            # Reformat (including units) if necessary.
            if val is None:
                if self.oldval == "":
                    self.dd.value = self.default
                return

            val = '{:~}'.format(val)
            if val != self.oldval:
                self.no_cb = True
                self.dd.value = val
                self.oldval = val
            return

        self.oldval = self.dd.value
        valid = self.check(val)
        # update the valid widget
        self.valid.value = valid
        if valid is False:
            return

        if self._cb is not None:
            val = '{:~}'.format(val)
            self._cb(self.name, val)

    @property
    def str(self):
        val = self.parse_expr(self.dd.value)
        if val is None:
            return None

        # if we reformat the displayed value, then update it
        if self.units is not None:
            val = '{:~}'.format(val)
        if val != self.oldval:
            self.no_cb = True
            self.dd.value = val
            self.oldval = val

        return val

    @property
    def value(self):
        val = self.parse_expr(self.dd.value)
        if val is None:
            return None

        # if we reformat the displayed value, then update it
        str_val = val
        if self.units is not None:
            str_val = '{:~}'.format(val)
        if str_val != self.oldval:
            self.no_cb = True
            self.dd.value = str_val
            self.oldval = str_val

        if self.units is None:
            return self.type(val)
        return val.magnitude

    @value.setter
    def value(self, newval):
        if newval is None:
            raise ValueError("Cannot set value to None")
        val = self.parse_expr(newval)
        if self.check(val) == False:
            raise ValueError("Range Error")
        if self.units is None:
            val = str(val)
        else:
            val = '{:~}'.format(val)
        self.dd.value = val

    def _ipython_display_(self):
        self.w._ipython_display_()

    @property
    def enabled(self):
        return not self.dd.disabled

    @enabled.setter
    def enabled(self, newval):
        self.dd.disabled = not newval

class Number(NumValue):
    def __init__(self, name, description, value, **kwargs):
        if type(value) != str:
            value = str(value)
        self.type = float
        self.dd = widgets.Text(value=value, width='auto')
        NumValue.__init__(self, name, description, **kwargs)


class Integer(NumValue):
    def __init__(self, name, description, value, **kwargs):
        if type(value) != int:
            value = int(value)
        self.type = int
        self.dd = widgets.IntText(value=value, width='auto')
        NumValue.__init__(self, name, description, **kwargs)
