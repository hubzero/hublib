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
    def __init__(self, wlist, **kwargs):
        """
        Creates a form from a list of ui elements

        :param wlist: List of UI elements
        :param name: Optional string to show in a titlebar or tab.
        :param desc: Optional description that will show in a popup over the titlebar.
        :param width: Optional with of the form.
        """
        self.name = kwargs.get('name', '')
        width = kwargs.get('width')
        desc = kwargs.get('desc', '')
        wlist = [w.w for w in wlist]

        if self.name:
            style = "style='background-color: #DCDCDC; font-size:200; padding: 5px'"
            if desc:
                desc = 'data-toggle="popover" title="%s"' % (desc)
            lval = '<p  %s %s>%s</p>' % (desc, style, self.name)
            label = widgets.HTML(value=lval, layout=widgets.Layout(flex='2 1 auto'))
            wlist.insert(0, label)

        self.w = widgets.VBox(wlist, layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width=width
        ))

    def _ipython_display_(self):
        self.w._ipython_display_()
