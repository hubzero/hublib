from __future__ import print_function
import ipywidgets as widgets
from IPython.display import display, Javascript


# recommended icons: download, arrow-circle-down, cloud-download
# icons come from http://fontawesome.io/icons/
# won't be visible on ipywidgets <  6.0

# success = green
# info = blue
# warning = orange
# danger = red

class Download(object):

    def __init__(self, filename, **kwargs):

        label = kwargs.get('label', filename)
        icon = kwargs.get('icon', '')
        tooltip = kwargs.get('tooltip', '')
        style = kwargs.get('style', '')
        bcb = kwargs.get('cb', None)

        self.w = widgets.Button(
            description=label,
            icon=icon,
            tooltip=tooltip,
            button_style=style
            )

        def button_cb(filename):

            js = Javascript("window.open('%s')" % filename)

            def cb(x):
                if bcb is not None:
                    bcb()
                display(js)
            return cb

        self.w.on_click(button_cb(filename))

    def _ipython_display_(self):
        self.w._ipython_display_()
