import ipywidgets as widgets


class Tab(object):
    def __init__(self, wlist, **kwargs):
        titles = kwargs.get('titles')
        if titles is None:
            titles = {i: w.name for i, w in enumerate(wlist)}
        else:
            titles = {i: w for i, w in enumerate(titles)}
        self.w = widgets.Tab([w.w for w in wlist], _titles=titles)
        self.wlist = wlist
        self._disabled = False

    def _ipython_display_(self):
        self.w._ipython_display_()

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, newval):
        for w in self.wlist:
            w.disabled = newval
        self._disabled = newval


class Form(object):
    def __init__(self, wlist, **kwargs):
        """
        Creates a form from a list of ui elements

        :param wlist: List of UI elements
        :param name: Optional string to show in a titlebar or tab.
        :param desc: Optional description that will show in a popup over the titlebar.
        :param width: Optional with of the form.
        """
        self.wlist = wlist
        self._name = kwargs.get('name', '')
        self._disabled = kwargs.get('disabled', False)
        self.hidden = []
        self._width = kwargs.get('width')
        self._desc = kwargs.get('desc', '')
        self._build()

    def _build(self):
        iwlist = [w.w for w in self.wlist]
        if self.name:
            style = "style='background-color: #DCDCDC; font-size:200; padding: 5px'"
            if self._desc:
                self._desc = 'data-toggle="popover" title="%s"' % (self._desc)
            lval = '<p  %s %s>%s</p>' % (self._desc, style, self.name)
            label = widgets.HTML(value=lval, layout=widgets.Layout(flex='2 1 auto'))
            iwlist.insert(0, label)

        self.w = widgets.VBox(iwlist, layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width=self.width
        ))

    def _ipython_display_(self):
        self.w._ipython_display_()

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, val):
        self._desc = val
        self._build()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val
        self._build()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self._build()

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, newval):
        for w in self.wlist:
            w.disabled = newval
        self._disabled = newval

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, newval):
        for w in self.wlist:
            w.visible = newval
        self._visible = newval
