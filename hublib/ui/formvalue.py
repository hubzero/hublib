import ipywidgets as widgets


class FormValue(widgets.HBox):

    def __init__(self, name, **kwargs):
        self.name = name
        width = kwargs.get('width', 'auto')
        self._ncb = kwargs.get('cb')

        # accept either 'description' or 'desc'
        desc = kwargs.get('desc', kwargs.get('description', ''))
        
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            padding='3px',
            width=width
        )

        self.dd.layout = {'width': 'initial'}
        self.dd.disabled = kwargs.get('disabled', False)
        self.dd.observe(self._cb, names='value')

        popup = '<div data-toggle="popover" title="%s" data-container="body">%s</div>' % (desc, name)
        label = widgets.HTML(value=popup, layout=widgets.Layout(flex='2 1 auto'))
        widgets.HBox.__init__(self, [label, self.dd], layout=form_item_layout)

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


class String(FormValue):
    def __init__(self, name, value, **kwargs):
        self.dd = widgets.Text(value=value)
        FormValue.__init__(self, name, **kwargs)


class Dropdown(FormValue):
    def __init__(self, name, options, value, **kwargs):
        self.dd = widgets.Dropdown(options=options, value=value)
        FormValue.__init__(self, name, **kwargs)
        mw = '{}ch'.format(max(map(len, self.dd.options))+4)
        self.dd.layout =  {'width':'auto', 'min_width': mw}

class Checkbox(FormValue):
    def __init__(self, name, **kwargs):
        value = kwargs.get('value', False)
        self.dd = widgets.Checkbox(value=value)
        FormValue.__init__(self, name, **kwargs)


class Radiobuttons(FormValue):
    def __init__(self, name, options, value, **kwargs):
        self.dd = widgets.RadioButtons(options=options, value=value)
        FormValue.__init__(self, name, **kwargs)


class Togglebuttons(FormValue):
    def __init__(self, name, options, value, **kwargs):
        self.dd = widgets.ToggleButtons(options=options, value=value)
        FormValue.__init__(self, name, **kwargs)
        # self.dd.style.button_width='{}ch'.format(max(map(len, self.dd.options))+4)
        self.dd.style={'button_width': 'initial'}


class Text(FormValue):
    def __init__(self, name, value='', **kwargs):
        self.dd = widgets.Textarea(value=value)
        FormValue.__init__(self, name, **kwargs)
