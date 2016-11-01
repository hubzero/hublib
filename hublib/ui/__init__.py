import ipywidgets as widgets
from numvalue import Number, Integer
from formvalue import String, Dropdown


class Tab(object):
    def __init__(self, wlist,):
        titles = {i: w.name for i, w in enumerate(wlist)}
        self.w = widgets.Tab([w.w for w in wlist], _titles=titles)

    def _ipython_display_(self):
        self.w._ipython_display_()


class Form(object):
    def __init__(self, wlist, name='', showtitle=False, **kwargs):
        """
        Creates a form from a list of ui elements

        :param wlist: List of UI elements
        :param name: Optional name. Default is ''.
        """
        self.name = name
        width = kwargs.get('width')
        desc = kwargs.get('desc')
        if desc is None:
            lval = "<p style='background-color: #DCDCDC; font-size:200; padding: 5px'>%s</p>" % name
        else:
            lval = '<p data-toggle="popover" title="%s">%s</p>' % (desc, name)
        label = widgets.HTML(value=lval, layout=widgets.Layout(flex='2 1 auto'))

        wlist = [w.w for w in wlist]
        wlist.insert(0, label)
        self.w = widgets.VBox(wlist, layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width=width
        ))

    def _ipython_display_(self):
        self.w._ipython_display_()
