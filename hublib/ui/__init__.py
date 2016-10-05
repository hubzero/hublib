import ipywidgets as widgets
from IPython.display import display, HTML
import pint


ureg = pint.UnitRegistry()
ureg.autoconvert_offset_to_baseunit = True

def find_unit(xpr):
    if hasattr(xpr, 'compatible_units'):
        return xpr
    return ureg.parse_expression(xpr).units


class Tab(object):
    def __init__(self, wlist,):
        titles = {i: w.name for i, w in enumerate(wlist)}
        self.tab = widgets.Tab([w.form for w in wlist], _titles=titles)

    def _ipython_display_(self):
        self.tab._ipython_display_()


class Form(object):
    def __init__(self, wlist, name=None):
        self.name = name
        self.form = widgets.VBox([w.w for w in wlist], layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width='50%'
        ))

    def _ipython_display_(self):
        self.form._ipython_display_()



label_layout = widgets.Layout(flex='1 1 auto')

form_item_layout = widgets.Layout(
   display='flex',
   flex_flow='row',
   border='solid 1px lightgray',
   justify_content='space-between'
)


class FormValue(object):

    def __init__(self, name, desc, **kwargs):
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
            self.min = self.type(self.conv_value(self.min, True))
        if self.max is not None:
            self.max = self.type(self.conv_value(self.max, True))

    def conv_value(self, val, magnitude=False):
        # print "conv_value", str(val), self.units
        if val is None or self.units is None:
            return val

        try:
            val = ureg.parse_expression(str(val))
            if hasattr(val, 'units'):
                val = val.to(self.units)
            elif self.units:
                val *= self.units
            if magnitude:
                return val.magnitude
            return val
        except:
            return None

    def check(self, val):
        # print "check", val, self.units, self.type
        if val is None:
            return False

        if self.units:
            mag = self.type(val.magnitude)
        else:
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
        # print "cb val=%s oldval=%s no_cb=%s" % (self.dd.value, self.oldval, self.no_cb)
        if self.no_cb:
            self.no_cb = False
            return

        val = self.conv_value(self.dd.value)

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
    def value(self):
        val = self.conv_value(self.dd.value)
        if val is not None:
            val = '{:~}'.format(val)
            if val != self.oldval:
                self.no_cb = True
                self.dd.value = val
                self.oldval = val
        return val

    @value.setter
    def value(self, newval):
        self.dd.value = newval
        self.dd.value = newval

    def _ipython_display_(self):
        self.w._ipython_display_()

    @property
    def enabled(self):
        return self.dd.disabled

    @enabled.setter
    def enabled(self, newval):
        self.dd.disabled = not newval


class Dropdown(FormValue):
    def __init__(self, name, description, options, value, **kwargs):
        self.dd = widgets.Dropdown(options=options, value=value, width='auto')
        self.type = str
        FormValue.__init__(self, name, description, **kwargs)


class Number(FormValue):
    def __init__(self, name, description, value, **kwargs):
        if type(value) != str:
            value = str(value)
        self.type = float
        self.dd = widgets.Text(value=value, width='auto')
        FormValue.__init__(self, name, description, **kwargs)

    @property
    def value(self):
        return float(self._value)

    @value.setter
    def value(self, newval):
        self._value = newval


class Integer(FormValue):
    def __init__(self, name, description, value, **kwargs):
        if type(value) != int:
            value = int(value)
        self.type = int
        self.dd = widgets.IntText(value=value, width='auto')
        FormValue.__init__(self, name, description, **kwargs)


class String(FormValue):
    def __init__(self, name, description, value, **kwargs):
        self.dd = widgets.Text(value=value, width='auto')
        self.type = str
        FormValue.__init__(self, name, description, **kwargs)
