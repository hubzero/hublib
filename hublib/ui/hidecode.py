from __future__ import print_function
import ipywidgets as widgets
from IPython.display import display, Javascript


# recommended icons: fa-code
# icons come from http://fontawesome.io/icons/
# won't be visible on ipywidgets <  6.0

# button style
# success = green
# info = blue
# warning = orange
# danger = red

class HideCodeButton(object):

    def __init__(self, **kwargs):

        label = kwargs.get('label', None)
        icon = kwargs.get('icon', '')
        tooltip = kwargs.get('tooltip', '')
        style = kwargs.get('style', '')
        bcb = kwargs.get('cb', None)
        runall = kwargs.get('RunAll', False)

        self.func = 'hide'

        if label is None:
            self.hlabel = "Hide Code Cells"
            self.slabel = "Show Code Cells"
        elif isinstance(label, list):
            self.hlabel, self.slabel = label
        elif isinstance(label, str):
            self.hlabel = self.slabel = label
        else:
            raise ValueError('label should be a string or list containing two strings')

        if style is None:
            self.hstyle = ''
            self.sstyle = ''
        elif isinstance(style, list):
            self.hstyle, self.sstyle = style
        elif isinstance(style, str):
            self.hstyle = self.sstyle = style
        else:
            raise ValueError('style should be a string or list containing two strings')

        self.w = widgets.Button(
            description=self.hlabel,
            icon=icon,
            tooltip=tooltip,
            button_style=self.hstyle
            )

        def button_cb(ignore):
            js = Javascript("$('div.input').%s()" % self.func)
            if self.func == 'hide':
                self.func = 'show'
                self.w.description = self.slabel
                self.w.button_style = self.sstyle
            else:
                self.func = 'hide'
                self.w.description = self.hlabel
                self.w.button_style = self.hstyle

            if bcb is not None:
                bcb()
            display(js)

        self.w.on_click(button_cb)

    def _ipython_display_(self):
        self.w._ipython_display_()


class RunAllButton(object):

    def __init__(self, **kwargs):

        label = kwargs.get('label', "Run All Cells")
        icon = kwargs.get('icon', '')
        tooltip = kwargs.get('tooltip', '')
        style = kwargs.get('style', '')
        bcb = kwargs.get('cb', None)
        hide = kwargs.get('hide', False)

        js = """
require(["base/js/namespace"],
    function(IPython) {
        IPython.notebook.execute_all_cells();
    }
);
"""
        if hide:
            js += "$('div.input').hide()"
        self.js = Javascript(js)

        self.w = widgets.Button(
            description=label,
            icon=icon,
            tooltip=tooltip,
            button_style=style
            )

        def button_cb(ignore):
            if bcb is not None:
                bcb()

            display(self.js)

        self.w.on_click(button_cb)

    def _ipython_display_(self):
        self.w._ipython_display_()
