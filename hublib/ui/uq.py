import ipywidgets as widgets
from .numvalue import parse_units

class UQValue(widgets.HBox):

    def __init__(self, name, value, **kwargs):

        width = kwargs.get('width', 'auto')
        self._ncb = kwargs.get('cb')

        # accept either 'description' or 'desc'
        self._desc = kwargs.get('desc', '')
        if self._desc == '':
            self._desc = kwargs.get('description', '')

        self.units_str, self.units_tex = parse_units(kwargs.get('units'))
        #self.format = kwargs.get('format') not implemented yet

        self.name = name
        self._min = kwargs.get('min')
        self._max = kwargs.get('max')

        style = {'description_width': '10ch'}

        # EXACT
        self.exact_check = widgets.Checkbox(indent=False, value=True,
                                            layout={'width': 'auto'})
        self.exact_val = widgets.BoundedFloatText(
            value=value,
            min=self._min,
            max=self._max,
            description='Value:',
            layout={'width': 'auto'},    
            style=style,

        )
        exact_box = widgets.HBox([self.exact_check, self.exact_val])

        # RANGE (Uniform)
        self.range_check = widgets.Checkbox(indent=False, 
                                            layout={'width': 'auto'})
        self.range_from = widgets.BoundedFloatText(
            value=value,
            min=self._min,
            max=self._max,
            description='From:',
            layout={'width': 'auto'},
            style=style
        )
        self.range_to = widgets.BoundedFloatText(
            value=value,
            min=self._min,
            max=self._max,
            description='To:',
            layout={'width': 'auto'},
            style=style
        )
        range_box = widgets.HBox([self.range_check, self.range_from, self.range_to])
        
        # Gaussian (Normal)
        self.norm_check = widgets.Checkbox(indent=False,
                                           layout={'width': 'auto'})
        self.norm_mean = widgets.BoundedFloatText(
            value=value,
            min=self._min,
            max=self._max,
            description='Mean:',
            layout={'width': 'auto'},
            style=style
        )
        self.norm_dev = widgets.BoundedFloatText(
            value=value * .1,
            min=0,
            max=value,
            description='Dev:',
            layout={'width': 'auto'},
            style=style
        )
        norm_box = widgets.HBox([self.norm_check, self.norm_mean, self.norm_dev])
        
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            # padding='5px',
            width=width
        )
        # self.value = value

        rbox = widgets.VBox([exact_box, range_box, norm_box])
        self.acc = widgets.Accordion([rbox], layout=form_item_layout)
        
        for w in [self.exact_val, self.norm_mean, self.norm_dev, self.range_from, self.range_to]:
            w.observe(self._cb, names='value')

        self.acc.set_title(0, '%s' % (value))
        self.acc.layout = {'width': 'auto'}
        self.acc.selected_index = None
        self.exact_check.observe(self._select, names='value')
        self.norm_check.observe(self._select, names='value')
        self.range_check.observe(self._select, names='value')
        self.label = None
        self._update()
        widgets.HBox.__init__(self, [self.label, self.acc, self.unit_label], layout=form_item_layout)

    def _update(self):
        desc = self._desc
        if self.units_str != '':
            desc += "\nValues must be in units of %s." % self.units_str

        if self._min is not None:
            desc += "\nMin: %s\tMax: %s\n" % (self._min, self._max)
        
        popup = '<div data-toggle="popover" title="%s" data-container="body">%s</div>' % (desc, self.name)
        if self.label is None:
            self.label = widgets.HTML(value=popup, layout=widgets.Layout(flex='2 1 auto'))
            self.unit_label = widgets.HTMLMath(value=self.units_tex, layout={'min_width': '6ch'})
            return
        self.label.value = popup
        self.unit_label.value = self.units_tex

    def _select(self, w):
        if w['new'] is False:
            return
        w = w['owner']
        if w == self.exact_check:
            self.range_check.value = False
            self.norm_check.value = False
            self.acc.set_title(0, str(self.exact_val.value))
        elif w == self.range_check:
            self.exact_check.value = False
            self.norm_check.value = False
            self.acc.set_title(0, '[%s - %s]' % (self.range_from.value, self.range_to.value))
        elif w == self.norm_check:
            self.range_check.value = False
            self.exact_check.value = False
            self.acc.set_title(0, '[Mean: %s Dev: %s]' % (self.norm_mean.value, self.norm_dev.value))

    def _cb(self, w):
        owner = w['owner']
        if self.exact_check.value and owner != self.exact_val:
            return
        if self.range_check.value:
            if owner != self.range_to and owner != self.range_from:
                return
        if self.norm_check.value:
            if owner != self.norm_dev and owner != self.norm_mean:
                return
        self.acc.set_title(0, str(self.value))
        if self._ncb is not None:
            self._ncb(self, self.value)

    @property
    def cb(self):
        return self._ncb

    @cb.setter
    def cb(self, newcb):
        self._ncb = newcb

    @property
    def value(self):
        if self.exact_check.value:
            return self.exact_val.value
        if self.norm_check.value:
            return '[Mean: %s Dev: %s]' % (self.norm_mean.value, self.norm_dev.value)
        return '[%s - %s]' % (self.range_from.value, self.range_to.value)

    @value.setter
    def value(self, newval):
        self.exact_val.value = float(newval)
        self.exack_check = True
        self.acc.set_title(0, str(newval))
        # FIXME: what about setting to norm or range?