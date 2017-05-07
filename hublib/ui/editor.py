from __future__ import print_function
import os
import ipywidgets as widgets
import base64
from IPython.display import HTML, Javascript, display
from string import Template
import json

# NOT FINISHED.  DO NOT USE

# https://ace.c9.io/build/kitchen-sink.html

js_load = """
<script>
requirejs.config({
    paths: {
        'ace': ['//cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/ace'],
    },
});

require(['ace'], function(ace) {
    console.log("Loaded :)");
    return {};
});
</script>
"""

js_template = """
<style type="text/css" media="screen">
#${editor} {
    margin-left: 15px;
    margin-top: 15px;
    height: ${height};
    width: ${width};
    border-style: ${border};
}
</style>

<div id="${editor}"></div>

<script>
var ${editor} = ace.edit("${editor}");
${editor}.setShowPrintMargin(false);
${editor}.setTheme("ace/theme/${theme}");
${editor}.getSession().setMode("ace/mode/${mode}");
document.getElementById("${editor}").style.fontSize="${fontsize}";
${editor}.setAutoScrollEditorIntoView(true);
</script>
"""


class Editor(object):

    num = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        if self.name == "":
            self.name = 'editor' + str(Editor.num)
            Editor.num += 1
        height = kwargs.get('height', '500px')
        width = kwargs.get('width', 'auto')
        border = kwargs.get('border', 'solid')
        theme = kwargs.get('theme', 'xcode')
        mode = kwargs.get('mode', 'python')
        fontsize = kwargs.get('fontsize', '14px')
        display(HTML(js_load))
        d = dict(height="500px",
                 width=width,
                 border=border,
                 editor=self.name,
                 theme=theme,
                 mode=mode,
                 fontsize=fontsize)
        temp = Template(js_template).substitute(d)
        display(HTML(temp))

    @property
    def desc(self):
        return ""

    @desc.setter
    def desc(self, val):
        return

    @property
    def value(self):
        global _tval
        temp = """var value = ${editor}.getValue();
        var cmd = "_tval = '''" + value + "'''";
        var kernel = IPython.notebook.kernel;
        kernel.execute(cmd);
        """
        temp = Template(temp).substitute({'editor': self.name})
        display(Javascript(temp))
        return _tval

    @value.setter
    def value(self, val):
        temp = """console.log(${text}); ${editor}.setValue(${text});"""
        temp = Template(temp).substitute(
            {'text': json.dumps(val),
             'editor': self.name})
        display(Javascript(temp))
