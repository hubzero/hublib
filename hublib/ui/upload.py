import time
import os
import ipywidgets as widgets
import base64

js_template = """
<script type="text/Javascript">
  function handle%s(evt) {
    var results, command;
    var kernel = IPython.notebook.kernel;
    var file = evt.target.files[0];
    console.log('file=', file);
    kernel.execute('from hublib.ui import FileUpload')
    var that = this;
    if (file) {
        var fileReader = new FileReader();
        fileReader.onload = function fileReaderOnload () {
            results = fileReader.result;
            cmd = 'FileUpload.fvals["%s"]["data"]="' + results + '"';
            console.log(cmd);
            kernel.execute(cmd);
        };
        fileReader.readAsDataURL(file);
    } else {
        console.log('Unable to open file.', file);
    }

    cmd = 'FileUpload.fvals["%s"]={}';
    cmd = cmd + ';FileUpload.fvals["%s"]["name"]="' + file.name + '"';
    console.log(cmd);
    kernel.execute(cmd);
  }

  document.getElementById('fs_%s').addEventListener('change', handle%s, false);
</script>
"""


class FileUpload(object):
    fvals = {}

    def __init__(self, name, desc, **kwargs):
        width = kwargs.get('width', 'auto')
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )
        self.accept = kwargs.get('accept')
        self.vname = FileUpload.make_vname()
        input_form = '<input type="file" id="fs_%s" name="files[]"/>' % self.vname
        js = js_template % (self.vname, self.vname, self.vname, self.vname, self.vname, self.vname)
        self.input = widgets.HTML(value=input_form + js,
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                  layout=widgets.Layout(flex='2 1 auto'))
        self.w = widgets.Box([self.label, self.input], layout=form_item_layout)

    def save(self, name=None):
        if self.name is None:
            raise IOError("No file or data found.")

        if name is None:
            name = self.name

        with open(name, 'w') as f:
            f.write(self.data)

        try:
            del FileUpload.fvals[self.vname]
        except:
            pass

    @property
    def name(self):
        if self.vname in FileUpload.fvals:
            return FileUpload.fvals[self.vname]['name']
        return None

    @property
    def data(self):
        if self.vname not in FileUpload.fvals:
            return None
        data = FileUpload.fvals[self.vname]['data']
        if type(data) == str and data.startswith('data:'):
            try:
                FileUpload.fvals[self.vname]['data'] = base64.b64decode(data.split(',', 1)[1])
            except:
                pass
        return FileUpload.fvals[self.vname]['data']

    def __del__(self):
        try:
            del FileUpload.fvals[self.vname]
        except:
            pass

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

    @staticmethod
    def make_vname():
        t = str(time.time()).replace('.', '_')
        return "v_%s" % t
