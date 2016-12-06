import ipywidgets as widgets


class FormValue(object):

    def __init__(self, name, desc, **kwargs):
        width = kwargs.get('width', 'auto')

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )

        cb = kwargs.get('cb')
        self.disabled = kwargs.get('disabled', False)
        self.default = self.dd.value
        self.label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.w = widgets.Box([self.label, self.dd], layout=form_item_layout)
        try:
            self.dd.on_submit(lambda x: self.cb(None))
        except:
            pass
        self.dd.observe(lambda x: self.cb(x['new']), names='value')

        self._cb = cb
        self.name = name
        self.no_cb = False

    def cb(self, _):
        '''
        Called when the value changed.  It is called after every keystroke, so
        we check on the fly and only reformat on <enter> or when the value property is read.
        '''

        val = self.dd.value
        # print "cb val=%s no_cb=%s" % (val, self.no_cb)
        if self.no_cb:
            self.no_cb = False
            return

        if self._cb is not None:
            self._cb(self.name, val)

    @property
    def value(self):
        return self.dd.value

    @value.setter
    def value(self, newval):
        try:
            self.dd.value = newval
        except:
            raise ValueError("Invalid value.")

    def _ipython_display_(self):
        self.w._ipython_display_()

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
            self.w.layout.visibility = 'visible'
            return
        self.dd.layout.visibility = 'hidden'
        self.w.layout.visibility = 'hidden'


class String(FormValue):
    def __init__(self, name, description, value, **kwargs):
        self.dd = widgets.Text(value=value, width='auto')
        FormValue.__init__(self, name, description, **kwargs)


class Dropdown(FormValue):
    def __init__(self, name, description, options, value, **kwargs):
        self.dd = widgets.Dropdown(options=options, value=value)
        FormValue.__init__(self, name, description, **kwargs)


class Checkbox(FormValue):
    def __init__(self, name, description, value, **kwargs):
        self.dd = widgets.Checkbox(value=value)
        FormValue.__init__(self, name, description, **kwargs)


class Radiobuttons(FormValue):
    def __init__(self, name, description, options, value, **kwargs):
        self.dd = widgets.RadioButtons(options=options, value=value)
        FormValue.__init__(self, name, description, **kwargs)


class Togglebuttons(FormValue):
    def __init__(self, name, description, options, value, **kwargs):
        self.dd = widgets.ToggleButtons(options=options, value=value)
        FormValue.__init__(self, name, description, **kwargs)


class Text(FormValue):
    def __init__(self, name, description, value='', **kwargs):
        self.dd = widgets.Textarea(value=value)
        FormValue.__init__(self, name, description, **kwargs)
