import ipywidgets as widgets
from numvalue import Number, Integer
from formvalue import FormValue

class Tab(object):
    def __init__(self, wlist,):
        titles = {i: w.name for i, w in enumerate(wlist)}
        self.w = widgets.Tab([w.w for w in wlist], _titles=titles)

    def _ipython_display_(self):
        self.w._ipython_display_()


class Form(object):
    def __init__(self, wlist, name=None, width=None):
        """
        Creates a form from a list of ui elements

        :param wlist: List of UI elements
        :param name: Optional name. Default None.
        """
        for w in wlist:
            print w, type(w)
        self.name = name
        self.w = widgets.VBox([w.w for w in wlist], layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width=width
        ))

    def _ipython_display_(self):
        self.w._ipython_display_()


class String(FormValue):
    def __init__(self, name, description, value, **kwargs):
        self.dd = widgets.Text(value=value, width='auto')
        FormValue.__init__(self, name, description, **kwargs)

class Dropdown(FormValue):
    def __init__(self, name, description, options, value, **kwargs):
        self.dd = widgets.Dropdown(options=options, value=value)
        NumValue.__init__(self, name, description, **kwargs)

