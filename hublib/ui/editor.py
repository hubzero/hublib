from __future__ import print_function
import ipywidgets as widgets
from IPython.display import HTML, Javascript, display
from string import Template
from traitlets import Unicode, Bool, Int

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
    console.log("ACE loaded :)");
    return {};
});
</script>
"""

css_template = """
<style type="text/css" media="screen">
#${editor} {
    margin-left: 15px;
    margin-top: 15px;
    height: ${height};
    width: ${width};
    border-style: ${border};
}
</style>
"""

js_template = """
<script>
requirejs.undef('editor');

define('editor', ["jupyter-js-widgets"], function(widgets) {

    var EditorView = widgets.DOMWidgetView.extend({

        // Render the view.
        render: function() {
            this.ignorex = false;
            this.ignorev = false;
            //console.log('RENDER '+this.model.get('name'));
            this.div = document.createElement('div');
            this.div.setAttribute('id', this.model.get('name'));
            this.el.appendChild(this.div);
            this.listenTo(this.model, 'change:state', this._state_changed, this);
            this.listenTo(this.model, 'change:theme', this._theme_changed, this);
            this.listenTo(this.model, 'change:mode', this._mode_changed, this);
            this.listenTo(this.model, 'change:value2', this._value2_changed, this);
            this.listenTo(this.model, 'change:showmargin', this._showmargin_changed, this);
            this.listenTo(this.model, 'change:fontsize', this._fontsize_changed, this);
            this.update();
        },
        update: function() {
            return EditorView.__super__.update.apply(this);
        },
        // Tell Backbone to listen to the change event of input controls
        events: {
            "change": "handle_color_change"
        },

        _state_changed: function() {
            var state = this.model.get('state')
            //console.log('state: ' + state );
            if (state == 'start') {
                var that = this;
                this._ed = ace.edit(this.model.get('name'));
                this._ed.getSession().on('change', function(e) {
                    if (that.ignorev == true) { return }
                    that.ignorex = true;
                    //console.log('CHANGE1');
                    that.model.set('value2', that._ed.getValue());
                    //console.log('CHANGE2');
                    that.touch();
                    //console.log('CHANGE3');
                    that.ignorex = false;
                });
            };
        },
        _theme_changed: function() {
            //console.log("theme " + this.model.get('theme'));
            this._ed.setTheme("ace/theme/"+this.model.get('theme'));
        },
        _mode_changed: function() {
            //console.log("mode " + this.model.get('mode'));
            this._ed.getSession().setMode("ace/mode/"+this.model.get('mode'));
        },
        _value2_changed: function() {
            //console.log('value2 ' + this.ignorex);
            if (this.ignorex == true) { return };
            var val = this.model.get('value2');
            //console.log('VALUE2 ' + val);
            this.ignorev = true;
            this._ed.setValue(val);
            this.ignorev = false;
            //console.log('VALUE2 DONE');
        },
        _showmargin_changed: function() {
            this._ed.setShowPrintMargin(this.model.get('showmargin'));
        },
        _fontsize_changed: function() {
            document.getElementById(this.model.get('name')).style.fontSize=this.model.get('fontsize');
        },

        // Callback for when the color is changed.
        handle_color_change: function(event) {
            console.log('SOMETHING CHNAGED');
            console.log(event);
        },
    });

    return {
        EditorView: EditorView
    };
});
</script>
"""


class EditorWidget(widgets.DOMWidget):

    display(HTML(js_load + js_template))
    _view_name = Unicode('EditorView').tag(sync=True)
    _view_module = Unicode('editor').tag(sync=True)
    name = Unicode('').tag(sync=True)
    theme = Unicode('').tag(sync=True)
    mode = Unicode('').tag(sync=True)
    showmargin = Bool(True).tag(sync=True)
    fontsize = Unicode('').tag(sync=True)
    state = Unicode('').tag(sync=True)
    value2 = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content):
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


class Editor(widgets.DOMWidget):
    num = 0

    def __init__(self, **kwargs):
        self.name = 'editor' + str(Editor.num)
        Editor.num += 1
        height = kwargs.get('height', '500px')
        width = kwargs.get('width', 'auto')
        border = kwargs.get('border', 'solid')
        self._theme = kwargs.get('theme', 'xcode')
        self._mode = kwargs.get('mode', 'python')
        self._fontsize = kwargs.get('fontsize', '14px')

        d = dict(height=height,
                 width=width,
                 border=border,
                 editor=self.name)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))
        self.ed = EditorWidget()
        self.ed.name = self.name
        # self.ed.observe(self.value_loading, names='value2')

    @property
    def value(self):
        return self.ed.value2

    @value.setter
    def value(self, val):
        self.ed.value2 = val

    @property
    def theme(self):
        return self.ed.theme

    @theme.setter
    def theme(self, val):
        self.ed.theme = val

    @property
    def mode(self):
        return self.ed.mode

    @mode.setter
    def mode(self, val):
        self.ed.mode = val

    @property
    def fontsize(self):
        return self.ed.fontsize

    @fontsize.setter
    def fontsize(self, val):
        self.ed.fontsize = val

    def _ipython_display_(self):
        self.ed._ipython_display_()
        self.ed.state = 'start'
        self.ed.theme = self._theme
        self.ed.mode = self._mode
        self.ed.showmargin = False
        self.ed.fontsize = self._fontsize
        self.ed.state = ''
