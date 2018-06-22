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
        else:
            num = int(numstr)
        return num 
    except: 
        raise ValueError("Cannot parse '%s'" % numstr) 


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
            this.listenTo(this.model, 'change:reset', this._reset, this);
            this.update();
        },

        events: {
            // List of events and their handlers.
            'change': 'handle_file_change'
        },

        _reset: function() {
            this.label.innerHTML = this.labelstr;
            this.label.prepend(this.icon);
            this.file.removeAttribute("disabled");
        },

        _send_changed: function() {
            var that = this;
            var send = this.model.get('send');
            var fnum = send[0];
            var offset = send[1];
            var chunk_size=64*1024;
            var reader;

            if (fnum == -1) {
                // ignore
                return
            }

            if (offset == 0) {
                this.model.set('sent', -1);
                this.touch();
            }

            // console.log('send: ' + fnum + ' ' + offset);
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
                if (event.target.error == null) {
                    var b64 = tob64(event.target.result);
                    that.model.set('data', b64);
                    that.model.set('sent', offset);
                    that.touch();
                } else {
                    console.log("Read error: " + event.target.error);
                    that.model.set('data', '');
                    that.model.set('sent', -2);
                    that.touch();
                }
                that.touch();
            }
        
            var chunk_reader = function (_offset, _f) {
                // console.log('CR' + ' ' + _f + ' ' + _offset);
                reader = new FileReader();
                var chunk = _f.slice(_offset, chunk_size + _offset);            
                reader.readAsArrayBuffer(chunk);
                reader.onload = reader_done;
            }
    
            // OK. request next chunk
            chunk_reader(offset, this.files[fnum]);
        },
        
        
        handle_file_change: function(evt) {

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
                this.file.removeAttribute("disabled");
            } else if (filenames.length == 1) {
                this.label.innerHTML = "  " + filenames[0][0];
                this.file.setAttribute('disabled', 'true');
            } else {
                this.label.innerHTML = "  " + filenames.length + " files selected";
                this.file.setAttribute('disabled', 'true');           
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
    reset = Bool(False).tag(sync=True)

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

    def __init__(self, 
                 name, 
                 desc, 
                 dir='tmpdir',
                 maxnum=1,
                 maxsize='1M', 
                 cb=None,
                 basic=False,
                 width='auto'):

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )
        basic_layout = widgets.Layout(
            flex='10 1 auto',
            width=width
        )
        self.input = FileWidget()
        if maxnum > 1:
            self.input.multiple = True
        self.maxnum = maxnum
        self.maxsize = to_bytes(maxsize)
        self.input.observe(self._filenames_received, names='filenames')
        self.input.observe(self._data_received, names='sent')
        self.basic = basic
        if basic:
            self.up = widgets.HBox([self.input], layout=basic_layout)
            self.w = widgets.HBox([self.up])
        else:
            label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                 layout=widgets.Layout(flex='2 1 auto'))

            self.up = widgets.HBox([label, self.input], layout=form_item_layout)
            self.w = widgets.VBox([self.up])

        self.dir = dir
        self.cb = cb
        self.prog = None
        self.fnames = []

    def _filenames_received(self, change):
        # We have received a list of files from the widget.
        # print('FILENAMES', len(change['new']), change['new'])
        num = len(change['new'])
        if num == 0:
            return

        # clear old progress bars, if any
        if self.prog:
            self.w.children = [self.up]
            del self.prog
            self.prog = None
            del self.progress

        self.fnames = []
        sizes = []
        self.nums = []
        for i, (name, sz) in enumerate(self.input.filenames):
            if sz > self.maxsize:
                print('File "%s" larger than maxsize.' % name, file=sys.stderr)
                continue
            self.fnames.append(name)
            sizes.append(sz)
            self.nums.append(i)

        if sizes == []:
            self.reset()        
            return

        # truncate list if necessary
        if len(self.fnames) > self.maxnum:
            print('Too many files selected (%s). Truncating...' % len(self.fnames), file=sys.stderr)

        self.fnames = self.fnames[:self.maxnum]

        self.prog = [pwidget(self.fnames[i], sizes[i], self.basic) for i in range(len(self.fnames))]
        self.progress = widgets.VBox(self.prog, layout={'width': '100%'})
        self.w.children = [self.up, self.progress]

        mkdir_p(self.dir)
        self.fnames = [os.path.join(self.dir, n) for n in self.fnames]

        self.f = open(self.fnames[0], 'wb')
        self.fnum = 0
        self.fcnt = 0
        self.input.send = [-1, 0]
        self.input.send = [self.nums[0], self.fcnt]
        # data_changed callback will handle the rest

    def _data_received(self, change):
        # print("_data_received")
        # process received blocks of data and request the next one until done.
        if change['new'] == -1:
            return
        if change['new'] == -2:
            # unexpected error
            self.prog[self.fnum].bar_style = 'error'
            print("Error downloading %s" % self.fnames[self.fnum], file=sys.stderr)
            return

        data = base64.b64decode(self.input.data)
        dlen = len(data)
        # print("GOT DATA (%d) [%d] for file %d" % (dlen, self.fcnt, self.fnum))
        if dlen == 0:
            self.prog[self.fnum].bar_style = 'success'
            self.f.close()
            if self.fnum >= len(self.fnames) - 1:
                # done with all downloads
                if self.cb:
                    self.cb(self, self.fnames)
                return
            self.fnum += 1
            self.f = open(self.fnames[self.fnum], 'wb')
            self.fcnt = 0
            self.input.send = [self.nums[self.fnum], self.fcnt]
            return
        self.f.write(data)
        self.fcnt += dlen
        self.prog[self.fnum].value = self.fcnt
        self.input.send = [self.nums[self.fnum], self.fcnt]

    def reset(self):
        # print("RESET", self)
        # Clear the filenames and progress bar(s)
        # Re-enable the upload widget
        if self.prog:
            self.w.children = [self.up]
            del self.prog
            self.prog = None
            del self.progress
        self.input.reset = True
        self.input.reset = False

    def list(self):
        return self.fnames

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


def pwidget(name, num, basic):
    if basic:
        return widgets.IntProgress(
            value=0,
            min=0,
            max=num,
            orientation='horizontal',
            layout=widgets.Layout(width='95%')
        )
    else:
        return widgets.IntProgress(
            value=0,
            min=0,
            max=num,
            description='%s:' % name,
            orientation='horizontal',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='95%')
        )


def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        if os.path.isdir(path):
            pass
        else:
            raise
