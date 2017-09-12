from __future__ import print_function
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
from string import Template
from traitlets import Unicode, Int, List

# A Really simple modal dialog widget using the bootstrap modal dialog.

css_template = """
<style type="text/css">

.modal-dialog {
    width: ${width};
}
"""

js_source = """
requirejs.undef('modal');
define('modal', ["base/js/dialog", "jupyter-js-widgets"], function(dialog, widgets) {
    var ModalView = widgets.DOMWidgetView.extend({
        render: function() {
            var that = this;
            var but = this.model.get('buttons');
            var primary = this.model.get('bprim');
            var buttons = {};
            for (var i = 0; i < but.length; i++) {
                if (i === primary) {
                    buttons[but[i]] = {class: 'btn-primary'};
                } else {
                    buttons[but[i]] = {};
                }
                (function(i) {
                    buttons[but[i]].click = function () {that.model.set('value', i); that.touch()};
                })(i);
            }
            dialog.modal({
                body: this.model.get('body'),
                title: this.model.get('title'),
                buttons: buttons
            })
        },
    });
    return {
        ModalView: ModalView
    };
});
"""


class Modal(widgets.DOMWidget):

    _view_name = Unicode('ModalView').tag(sync=True)
    _view_module = Unicode('modal').tag(sync=True)
    value = Int(-1).tag(sync=True)
    buttons = List(['OK']).tag(sync=True)
    bprim = Int(0).tag(sync=True)
    body = Unicode('').tag(sync=True)
    title = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):

        display(Javascript(js_source))

        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)
        bcb = kwargs.get('cb', None)
        self.bprim = self.check_primary(kwargs.get('primary', 'OK'))
        self.cb = kwargs.get('cb')
        if self.cb:
            self.observe(self._cb, names='value')

        width = kwargs.get('width', '50%')
        d = dict(width=width)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))

    def _cb(self, change):
        self.cb(change['new'])

    def check_primary(self, p):
        # primary sets the highlighted dialog button.
        # it must be valid index or name of a button
        if p in self.buttons:
            return self.buttons.index(p)

        if type(p) == int and p >= 0 and p < len(self.buttons):
            return p

        raise ValueError('Primary must by an index or button string.')
