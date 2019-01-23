import ipywidgets as widgets
from .. import ureg



# xpr - pint quantity, pint unit or str
# may be unicode string
# 
# Returns string for description and
# a string for unit label, which may be latex.


def parse_units(xpr):
    if xpr is None or xpr == '':
        return '', ''
    try:
        u = xpr.units
        us = str(u)
        ul = '{:~L}'.format(u)
    except:
        try:
            u = ureg.parse_expression(xpr).units
            us = str(u)
            ul = '{:~L}'.format(u)
        except:
            try:
                us = str(xpr)
                ul = '{:~L}'.format(xpr)
            except:
                return xpr, xpr
    if ul.startswith('\\'):
        ul = '$' + ul + '$'
    return us, ul


class NumValue(widgets.HBox):

    def _create_widget(self, ntype, value, min, max):

        if min is not None and max is None:
            raise ValueError("Min is set but not Max.")
        if min is None and max is not None:
            raise ValueError("Max is set but not Min.")

        if ntype == 'int':
            if min is not None:
                return widgets.BoundedIntText(value=value, min=min, max=max)
            return widgets.IntText(value=value)
        if min is not None:
            return widgets.BoundedFloatText(value=value, min=min, max=max)
        return widgets.FloatText(value=value)

    def __init__(self, ntype, name, value, **kwargs):

        width = kwargs.get('width', 'auto')
        self._ncb = kwargs.get('cb')

        # accept either 'description' or 'desc'
        self._desc = kwargs.get('desc', '')
        if self._desc == '':
            self._desc = kwargs.get('description', '')

        self.units_str, self.units_tex = parse_units(kwargs.get('units'))

        self.name = name
        _min = kwargs.get('min')
        _max = kwargs.get('max')

        self.dd = self._create_widget(ntype, value, _min, _max)
        self.dd.layout = {'width': 'auto'}
        self.dd.disabled = kwargs.get('disabled', False)
        self.dd.observe(self._cb, names='value')
        self.dd.min = _min
        self.dd.max = _max

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            padding='5px',
            width=width
        )
        self.label = None
        self._update()
        widgets.HBox.__init__(self, [self.label, self.dd, self.unit_label], layout=form_item_layout)

    def _update(self):
        desc = self._desc
        if self.units_str != '':
            desc += "\nValues must be in units of %s." % self.units_str

        if self.dd.min is not None:
            desc += "\nMin: %s\tMax: %s\n" % (self.dd.min, self.dd.max)
        
        popup = '<div data-toggle="popover" title="%s" data-container="body">%s</div>' % (desc, self.name)
        if self.label is None:
            self.label = widgets.HTML(value=popup, layout=widgets.Layout(flex='2 1 auto'))
            self.unit_label = widgets.HTMLMath(value=self.units_tex, layout={'min_width': '6ch'})
            return
        self.label.value = popup
        self.unit_label.value = self.units_tex

    def _cb(self, w):
        if self._ncb is not None:
            return self._ncb(self, w['new'])

    @property
    def cb(self):
        return self._ncb

    @cb.setter
    def cb(self, newcb):
        self._ncb = newcb
    
    @property
    def min(self):
        return self.dd.min

    @min.setter
    def min(self, val):
        self.dd.min = val
        self._update()

    @property
    def max(self):
        return self.dd.max

    @max.setter
    def max(self, val):
        self.dd.max = val
        self._update()

    @property
    def value(self):
        return self.dd.value

    @value.setter
    def value(self, newval):
        self.dd.value = newval

    @property
    def disabled(self):
        return self.dd.disabled

    @disabled.setter
    def disabled(self, newval):
        self.dd.disabled = newval

    @property
    def visible(self):
        return self.dd.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.dd.layout.visibility = 'visible'
            self.layout.visibility = 'visible'
            return
        self.dd.layout.visibility = 'hidden'
        self.layout.visibility = 'hidden'


class Number(NumValue):
    def __init__(self, name, value, **kwargs):
        NumValue.__init__(self, 'float', name, value, **kwargs)


class Integer(NumValue):
    def __init__(self, name, value, **kwargs):
        NumValue.__init__(self, 'int', name, value, **kwargs)
