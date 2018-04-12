# ----------------------------------------------------------------------
# A file upload widget for Jupyter
# ======================================================================
#  AUTHOR: Martin Hunt, Purdue University
#  Copyright (c) 2018  HUBzero Foundation, LLC
#  See LICENSE file for details.
# ======================================================================
from __future__ import print_function
import ipywidgets as widgets
import base64
import os
import sys
import time
from IPython.display import display, Javascript
from traitlets import List, Unicode, Bool, Int, List


js_template = """
requirejs.undef('filepicker');

define('filepicker', ["@jupyter-widgets/base"], function(widgets) {

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
            this.icon.setAttribute("class", "fa fa-upload");

            if (this.file.multiple) {
                this.labelstr = "  Upload Files";
            } else {
                this.labelstr = "  Upload File";
            }
            this.label.innerHTML = this.labelstr;
            this.label.prepend(this.icon);
            this.el.appendChild(this.label);
            this.el.appendChild(this.file);
            this.listenTo(this.model, 'change:send', this._send_changed, this);
            this.update();
        },

        events: {
            // List of events and their handlers.
            'change': 'handle_file_change'
        },

        _send_changed: function() {
            var that = this;
            var send = this.model.get('send');
            var fnum = send[0];
            var offset = send[1];
            var chunk_size=64*1024;
            
            if (offset == 0) {
                this.model.set('sent', -1);
                this.touch();
            }

            //console.log('send: ' + fnum + ' ' + offset);
            function tob64( buffer ) {
                var binary = '';
                var bytes = new Uint8Array( buffer );
                var len = bytes.byteLength;
                for (var i = 0; i < len; i++) {
                    binary += String.fromCharCode( bytes[ i ] );
                }
                return window.btoa( binary );
            }

            var reader_done = function (event) {
                // chunk is finished.  Send to python
                //console.log(event);
                if (event.target.error == null) {
                    var b64 = tob64(event.target.result);
                    that.model.set('data', b64);
                    that.model.set('sent', offset);
                } else {
                    console.log("Read error: " + event.target.error);
                    that.model.set('data', '');
                    that.model.set('sent', -2);
                }
                that.touch();
            }
        
            var chunk_reader = function (_offset, _f) {
                // console.log('CR' + ' ' + _f + ' ' + _offset);
                var reader = new FileReader();
                var chunk = _f.slice(_offset, chunk_size + _offset);            
                reader.readAsArrayBuffer(chunk);
                reader.onload = reader_done;
            }
    
            // OK. request next chunk
            chunk_reader(offset, this.files[fnum]);
        },
        
        
        handle_file_change: function(evt) {

            var that = this;
            var _files = evt.target.files;
            var filenames = [];
            var file_readers = [];
            this.files = [];

            for (var i = 0; i < _files.length; i++) {
                var file = _files[i];
                console.log("Filename: " + file.name);
                console.log("Type: " + file.type);
                console.log("Size: " + file.size + " bytes");
                this.files.push(file);
                filenames.push([file.name, file.size]);
            };

            // Set the filenames of the files.
            this.model.set('filenames', filenames);
            this.touch();

            // update the label
            if (filenames.length == 0) {
                this.label.innerHTML = this.labelstr;
            } else if (filenames.length == 1) {
                this.label.innerHTML = "  " + filenames[0][0];
            } else {
                this.label.innerHTML = "  " + filenames.length + " files selected";
            };
            this.label.prepend(this.icon);
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
    multiple = Bool(False).tag(sync=True)
    data = Unicode().tag(sync=True)
    send = List([]).tag(sync=True)
    sent = Int().tag(sync=True)

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
        self.input.observe(self._filenames_received, names='filenames')
        self.input.observe(self._data_received, names='sent')
        self.label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.up = widgets.HBox([self.label, self.input], layout=form_item_layout)
        self.w = widgets.VBox([self.up])
        self.prog = None

    def _filenames_received(self, change):
        # print('FILENAMES', len(change['new']), change['new'])
        num = len(change['new'])
        if num == 0:
            return
        if self.prog:
            self.w.children = [self.up]
            del self.prog
            self.prog = None
            del self.progress
        if self.cb:
            self.cb(change['new'])

    def _data_received(self, change):
        if change['new'] == -1:
            return
        if change['new'] == -2:
            # unexpected error
            self.prog[self.fnum].bar_style='error'
            print("Error downloading %s" % self.fnames[self.fnum], file=sys.stderr)
            return

        data = base64.b64decode(self.input.data)
        dlen = len(data)
        # print("GOT DATA (%d) [%d] for file %d" % (dlen, self.fcnt, self.fnum))
        if dlen == 0:
            self.prog[self.fnum].bar_style='success'
            self.f.close()
            if self.fnum >= len(self.fnames) - 1:
                # done with all downloads
                if self.rec_cb:
                    self.rec_cb(self.fnames)
                return
            self.fnum += 1
            self.f = open(self.fnames[self.fnum], 'wb')
            self.fcnt = 0
            self.input.send = [self.fnum, self.fcnt]
            return
        self.f.write(data)
        self.fcnt += dlen
        self.prog[self.fnum].value = self.fcnt
        self.input.send = [self.fnum, self.fcnt]

    def list(self, sizes=False):
        if sizes:
            return self.input.filenames
        return [f[0] for f in self.input.filenames]

    def save(self, name=None, dir=None, cb=None):
        self.fnames = [n[0] for n in self.input.filenames]
        numfiles = len(self.fnames)
        if numfiles == 0:
            return
        if name and numfiles != 1:
            print("'name' should not be set for multiple file uploads.", file=sys.stderr)
            return

        self.rec_cb = cb
        sizes = [n[1] for n in self.input.filenames]
        self.prog = [pwidget(self.fnames[i], sizes[i]) for i in range(len(self.fnames))]
        self.progress = widgets.VBox(self.prog)
        self.w.children = [self.up, self.progress]

        if name:
            self.fnames = [name]

        if dir:
            mkdir_p(dir)
            self.fnames = [os.path.join(dir, n) for n in self.fnames]

        self.f = open(self.fnames[0], 'wb')
        self.fnum = 0
        self.fcnt = 0
        self.input.send = [self.fnum, self.fcnt]
        # data_changed callback will handle the rest

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


def pwidget(name, num):
    return widgets.IntProgress(
        value=0,
        min=0,
        max=num,
        description='%s:' % name,
        orientation='horizontal',
        style = {'description_width': 'initial'},
        layout = widgets.Layout(width='95%')
    )


def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        if os.path.isdir(path):
            pass
        else:
            raise