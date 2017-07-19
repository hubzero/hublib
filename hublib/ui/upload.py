from __future__ import print_function
import ipywidgets as widgets
import base64
import sys
from IPython.display import display, Javascript
from traitlets import List, Unicode, Bool, Int


def to_bytes(numstr):
    try:
        if isinstance(numstr, int):
            return numstr
        last = numstr[-1]
        if last == 'B':
            numstr = numstr[:-1]
            last = numstr[-1]
        num = int(numstr[:-1])
        if last == 'G':
            num *= 1024**3
        elif last == 'M':
            num *= 1024**2
        elif last == 'K':
            num *= 1024
        return num
    except:
        raise ValueError("Cannot parse '%s'" % numstr)


js_template = """
requirejs.undef('filepicker');

define('filepicker', ["jupyter-js-widgets"], function(widgets) {

    var FilePickerView = widgets.DOMWidgetView.extend({
        render: function(){
            this.file = document.createElement('input');
            this.file.setAttribute('class', 'fileinput');
            this.file.setAttribute('id', this.cid);
            this.file.multiple = this.model.get('multiple');
            this.file.required = true;
            this.file.setAttribute('type', 'file');
            this.file.setAttribute('style', 'display:none');

            this.label = document.createElement('label');
            this.label.setAttribute('for', this.cid);
            this.label.setAttribute('style', 'border: 1px solid; border-radius: 5px; display: inline-block; padding: 6px 12px');

            this.icon = document.createElement('i');
            this.icon.setAttribute("class", "fs fa-upload");

            if (this.file.multiple) {
                this.labelstr = "  Upload Files";
            } else {
                this.labelstr = "  Upload File";
            }
            this.label.innerHTML = this.labelstr;
            this.label.prepend(this.icon);
            this.el.appendChild(this.label);
            this.el.appendChild(this.file);
            this.update();
        },

        events: {
            // List of events and their handlers.
            'change': 'handle_file_change',
        },

        handle_file_change: function(evt) {

            var that = this;
            var files = evt.target.files;
            var filenames = [];
            var skipped = [];
            var file_readers = [];

            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                console.log("Filename: " + file.name);
                console.log("Type: " + file.type);
                console.log("Size: " + file.size + " bytes");
                if (file.size > this.model.get('maxsize')) {
                    skipped.push(file.name);
                    continue;
                };
                filenames.push(file.name);

                // Read the file's textual content and set value_i to those contents.
                file_readers.push(new FileReader());
                file_readers[i].onload = (function(file, i) {
                    return function(e) {
                        that.model.set('value_' + i, e.target.result);
                        that.touch();
                        console.log("file_" + i + " loaded: " + file.name);
                    };
                })(file, i);
                file_readers[i].readAsDataURL(file);
            };

            // update the label
            if (filenames.length == 0) {
                this.label.innerHTML = this.labelstr;
            } else if (filenames.length == 1) {
                this.label.innerHTML = "  " + filenames[0];
            } else {
                this.label.innerHTML = "  " + filenames.length + " files selected";
            };
            this.label.prepend(this.icon);

            // Set the filenames of the files.
            this.model.set('filenames', filenames);
            this.model.set('skipped', skipped);
            this.touch();
        },
    });

    // Register the FilePickerView with the widget manager.
    return {
        FilePickerView: FilePickerView
    };
});
"""


class FileWidget(widgets.DOMWidget):
    display(Javascript(js_template))
    _view_name = Unicode('FilePickerView').tag(sync=True)
    _view_module = Unicode('filepicker').tag(sync=True)
    filenames = List([]).tag(sync=True)
    skipped = List([]).tag(sync=True)
    multiple = Bool(False).tag(sync=True)
    maxsize = Int(1024*1024).tag(sync=True)

    def __init__(self, **kwargs):

        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)

        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


class FileUpload(object):

    def __init__(self, name, desc, **kwargs):
        width = kwargs.get('width', 'auto')
        self.cb = kwargs.get('cb')
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )

        self.input = FileWidget()
        self.input.multiple = kwargs.get('multiple', False)
        self.input.maxsize = to_bytes(kwargs.get('maxsize', 1024*1024))
        self.input.observe(self.file_loading, names='filenames')
        self.input.observe(self.file_skipped, names='skipped')
        self.label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.w = widgets.Box([self.label, self.input], layout=form_item_layout)

    def file_loading(self, change):
        # print('LOADING', len(change['new']), change['new'])
        num = len(change['new'])
        if num == 0:
            return

        self.input.data = num * [None]
        traits = [('value_%d' % i, Unicode().tag(sync=True)) for i in range(num)]
        self.input.add_traits(**dict(traits))

        for i in range(num):
            self.input.observe(self.file_loaded, 'value_%d' % i)

    def file_skipped(self, change):
        for f in change['new']:
            print('Skipping "%s" due to size limit.' % f, file=sys.stderr)

    def file_loaded(self, change):
        # print("file_loaded '%s' (%s)" % (change['name'], len(change['new'])))
        if len(change['new']) == 0 or change['name'] == '':
            return
        i = int(change['name'].split('_')[1])
        fname = self.input.filenames[i]
        self.input.data[i] = base64.b64decode(change['new'].split(',', 1)[1])
        if self.cb:
            self.cb(fname, self.input.data[i])

    def list(self, sizes=False):
        res = []
        for i, f in enumerate(self.input.filenames):
            if sizes:
                res.append((f, len(self.input.data[i])))
            else:
                res.append(f)
        return res

    def save(self, name=None, num=0):
        if name is None:
            name = self.input.filenames[num]

        with open(name, 'wb') as f:
            f.write(self.input.data[num])

    def name(self, num=0):
        return self.input.filenames[num]

    def data(self, num=0):
        return self.input.data[num]

    @property
    def visible(self):
        return self.w.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.w.layout.visibility = 'visible'
            return
        self.w.layout.visibility = 'hidden'

    def _ipython_display_(self):
        self.w._ipython_display_()
