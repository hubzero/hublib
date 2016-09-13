import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

from IPython.utils.shimmodule import ShimWarning
warnings.simplefilter('ignore', ShimWarning)

import matplotlib
matplotlib.use('nbagg')
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from string import Template
import h5py
import puq

# ipython stuff
try:
    from ipywidgets import VBox, Dropdown, FloatText, Text, Tab, IntSlider, interact, interactive, interact_manual
    import ipywidgets as widgets
    from traitlets import Unicode
except:
    from IPython.html.widgets import VBox, Dropdown, FloatText, Text, Tab, IntSlider, interact, interactive, interact_manual
    from IPython.html import widgets
    from IPython.utils.traitlets import Unicode

from IPython.display import display, Image, HTML, YouTubeVideo, Javascript
from contextlib import contextmanager
from os.path import dirname, realpath, join


input_form = "<button name=\"%s,%s\" class=\"continue_button\" onclick=\"IPython.wait_button_clicked()\">%s</button>"



from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic)


@register_line_magic
def wait(line):
    """ Set a waitpoint.  Optional line should contain a
    button name and wait name seperated by a comma"""
    line = line.split(',')
    if len(line) == 0:
        name = 'Run'
        wname = 'Running'
    elif len(line) == 1:
        name = line
        wname = 'Running'
    else:
        name, wname = line
    button = input_form % (name, wname, name)
    display(HTML(button))


@register_line_magic
def waitdone(line):
    """
    Does nothing now.  Might have a button to Restart.
    """
    display(HTML('DONE'))

# We delete these to avoid name conflicts for automagic to work
del wait
del waitdone


# plotly stuff
# (*) To communicate with Plotly's server, sign in with credentials file
import plotly.plotly as py
# (*) Useful Python/Plotly tools
import plotly.tools as tls
# (*) Graph objects to piece together plots
from plotly.graph_objs import *

# load code-folding extension
# get_ipython().run_cell_magic('javascript', '', "IPython.load_extensions('IPython-notebook-extensions-3.x/usability/codefolding/main');")

class UQVar:

    def __init__(self, name, label, state, a, b=1):
        self.name = name
        self.label = label
        self.w = Dropdown(
            options=['Exact', 'Gaussian', 'Uniform'],
            description='%s:' % label,
            value=state)

        self.w1 = FloatText(value=a, description='mean:')
        self.w2 = FloatText(value=b, description='dev:')
        self.form = VBox(children=[self.w, self.w1, self.w2],
                         padding=10,
                         border_width=5)
        self.w.on_trait_change(self.on_value_change, 'value')
        self.on_value_change('')

    def on_value_change(self, v):
        value = self.w.value
        if value == 'Exact':
            self.w2.visible = False
            self.w1.description = 'value:'
        elif value == 'Gaussian':
            self.w1.description = 'mean:'
            self.w2.description = 'dev:'
            self.w2.visible = True
        else:
            self.w1.description = 'min:'
            self.w2.description = 'max:'
            self.w2.visible = True

    @property
    def value(self):
        value = self.w.value
        if value == 'Exact':
            return [self.name, self.label, self.w1.value]
        if value == 'Gaussian':
            return puq.NormalParameter(self.name, self.label, mean=self.w1.value, dev=self.w2.value)
        if value == 'Uniform':
            return puq.UniformParameter(self.name, self.label, min=self.w1.value, max=self.w2.value)
        return None


def uqrun(**kwargs):
    u = UQRun(kwargs)
    return u

class UQRun:
    def __init__(self, uq_type, uq_args, cmd, varlist, outfiles=[], newdir=False):
        self.fname = 'foo.hdf5'

        cmd_t = Template(cmd)
        newlist = []
        for v in varlist:
            if not isinstance(v, puq.Parameter):
                cmd = cmd_t.safe_substitute({v[0]: v[2]})
                cmd_t = Template(cmd)
            else:
                newlist.append(v)
        varlist = newlist
        uq = puq.Smolyak(varlist, level=uq_args)
        host = puq.InteractiveHost()
        prog = puq.TestProgram(exe=cmd, outfiles=outfiles, newdir=newdir)
        sw = puq.Sweep(uq, host, prog)
        sw.run(self.fname, overwrite=True)
        self.hf = h5py.File(self.fname, 'r')

    def plot_responses(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            rf.plot(title=False)
        plt.show()

    def plot_pdfs(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            rf.pdf(fit=False).plot()
        plt.show()

    def plotly_pdfs(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            pdf = rf.pdf(fit=False)
            trace1 = Scatter(
                x=pdf.x,
                y=pdf.y,
                mode='lines'
            )
        data = Data([trace1])
        return py.iplot(data, filename='PDF')

    def plotly_responses(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            return plot_ly(rf)

    def __del__(self):
        self.hf.close()

"""
class FileWidget(widgets.DOMWidget):
    _view_name = Unicode('FilePickerView', sync=True)
    value = Unicode(sync=True)
    filename = Unicode(sync=True)

    def __init__(self, **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs) # Call the base.

        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)
        get_ipython().run_cell_magic(u'javascript', u'', u'\nrequire(["widgets/js/widget", "widgets/js/manager"], function(widget, manager){\n\n    var FilePickerView = widget.DOMWidgetView.extend({\n        render: function(){\n            // Render the view.\n            this.setElement($(\'<input />\')\n                .attr(\'type\', \'file\'));\n        },\n        \n        events: {\n            // List of events and their handlers.\n            \'change\': \'handle_file_change\',\n        },\n       \n        handle_file_change: function(evt) { \n            // Handle when the user has changed the file.\n            \n            // Retrieve the first (and only!) File from the FileList object\n            var file = evt.target.files[0];\n            if (file) {\n\n                // Read the file\'s textual content and set value to those contents.\n                var that = this;\n                var file_reader = new FileReader();\n                file_reader.onload = function(e) {\n                    that.model.set(\'value\', e.target.result);\n                    that.touch();\n                }\n                file_reader.readAsText(file);\n            } else {\n\n                // The file couldn\'t be opened.  Send an error msg to the\n                // back-end.\n                this.send({ \'event\': \'error\' });\n            }\n\n            // Set the filename of the file.\n            this.model.set(\'filename\', file.name);\n            this.touch();\n        },\n    });\n        \n    // Register the DatePickerView with the widget manager.\n    manager.WidgetManager.register_widget_view(\'FilePickerView\', FilePickerView);\n});')

    def _handle_custom_msg(self, content):
        '''Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg.'''
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)
"""

def plot_ly(rfz):
    steps=40
    x = np.linspace(*rfz.vars[0][1], num=steps+1)
    y = np.linspace(*rfz.vars[1][1], num=steps+1)
    xx = np.meshgrid(x, y)
    ptsxy = np.vstack(map(np.ndarray.flatten, xx)).T
    pts = np.array(rfz.evala(ptsxy))
    fig = plt.figure()
    ax = Axes3D(fig, azim=30, elev=30)
    X, Y = xx
    Z = pts.reshape(X.shape)
    trace1 = Surface(
        z=Z,
        x=X,
        y=Y,
        #colorscale='YIGnBu'
        colorscale='Jet',
    )

    trace1b = dict(x=X, y=Y, z=Z, type='surface', colorscale='Jet', opacity=0.999)
    trace2 = Scatter3d(
        z=rfz.data[:,2],  # link the fxy 2d numpy array
        x=rfz.data[:,0],  # link 1d numpy array of x coords
        y=rfz.data[:,1],  # link 1d numpy array of y coords
        name='Actual',
        mode='markers',
        marker=Marker(
            size='4',
            color='black',
        )
    )
    # Package the trace dictionary into a data object
    data = Data([trace1, trace2])

    # Dictionary of style options for all axes
    axis = dict(
        showbackground=True, # (!) show axis background
        backgroundcolor="rgb(204, 204, 204)", # set background color to grey
        gridcolor="rgb(255, 255, 255)",       # set grid line color
        zerolinecolor="rgb(255, 255, 255)",   # set zero grid line color
    )

    # Make a layout object
    layout = Layout(
        title='Response', # set plot title\
        autosize=False,
        width=1200,
        height=1024,
        scene=Scene(  # (!) axes are part of a 'scene' in 3d plots
            xaxis=XAxis(axis), # set x-axis style
            yaxis=YAxis(axis), # set y-axis style
            zaxis=ZAxis(axis)  # set z-axis style
        )
    )

    # Make a figure object
    fig = Figure(data=data, layout=layout)

    # (@) Send to Plotly and show in notebook
    #py.iplot(fig, filename='response_surface2')
    return py.iplot([trace1b, trace2], validate=False, layout=layout, filename='response_surface')


def set_figsize(x=11, y=4):
    pylab.rcParams['figure.figsize'] = x, y


@contextmanager
def figsize(x=11, y=4):
    '''Temporarily set the figure size using 'with figsize(a, b):'

    '''
    size = pylab.rcParams['figure.figsize']
    set_figsize(x, y)
    yield
    pylab.rcParams['figure.figsize'] = size


def load_theme(dir='themes', name='custom.css'):
    f = join(dir, name)
    style = open(f, 'r').read()
    return HTML(style)


def prefix(url):
    prefix = '' if url.startswith('http') else 'http://'
    return prefix + url


def simple_link(url, name=None):
    name = url if name is None else name
    url = prefix(url)
    return '<a href="%s">%s</a>' % (url, name)


def html_link(url, name=None):
    return HTML(simple_link(url, name))


# Utility functions
def website(url, name=None, width='100%', height=450):
    html = []
    name = url if name == 'auto' else name
    if name:
        html.extend(['<div style="margin-bottom:10px">',
                     simple_link(url, name),
                     '</div>'] )

    html.append('<iframe src="%s"  width="%s" height="%s">' %
                (prefix(url), width, height))
    html.append('</iframe>')
    return HTML('\n'.join(html))


def nbviewer(url=None, gist=None, name=None, width='100%', height=450):
    if url:
        return website('nbviewer.ipython.org/url/' + url, name, width, height)
    elif gist:
        return website('nbviewer.ipython.org/' + str(gist), name, width, height)

