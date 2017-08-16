from __future__ import print_function
import ipywidgets as widgets
import base64
import sys
from IPython.display import display, Javascript, HTML
from string import Template

from traitlets import List, Unicode, Bool, Int

css_template = """
<style type="text/css">

.lmheader {
    border: solid;
    display: table;
    width: ${width};
}

.lmheader:after {
    content: "";
    display: table;
    clear: both;
}

.lmaddBtn {
    padding: 10px;
    background: #d9d9d9;
    color: #555;
    float: right;
    text-align: center;
    cursor: pointer;
    transition: 0.3s;
}

.lmaddIcon {
    padding: 10px;
    background: #d9d9d9;
    color: #555;
    float: right;
    text-align: center;
    cursor: pointer;
    transition: 0.3s;
}

.lmaddBtn:hover {
    background-color: #bbb;
}
.lmaddIcon:hover {
    background-color: #bbb;
}

/* Remove margins and padding from the list */
.lmUL {
    margin: 0;
    padding: 0;
}

/* Style the list items */
.lmUL li {
    cursor: pointer;
    position: relative;
    padding: 12px 8px 12px 40px;
    background: #eee;
    transition: 0.2s;
    width: ${width};

    /* make the list items unselectable */
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

/* Set all odd list items to a different color (zebra-stripes) */
.lmUL li:nth-child(odd) {
    background: #f9f9f9;
}

/* Darker background-color on hover */
.lmUL li:hover {
    background: #ddd;
}

</style>

"""


js_template = """
requirejs.undef('listmanager');

define('listmanager', ["jupyter-js-widgets"], function(widgets) {

    var ListManagerView = widgets.DOMWidgetView.extend({
        render: function(){
            this.div = document.createElement('div');
            this.div.setAttribute('class', 'lmheader');
            this.input = document.createElement('input')
            this.input.setAttribute('type', 'text');
            this.input.setAttribute('placeholder', this.model.get('list_text'));
            this.input.setAttribute('style', 'border: none; float: left; width: 90%; padding: 10px');
            this.span = document.createElement('span')

            if (this.model.get('button_text') === ''){
                this.span.setAttribute('class', 'lmaddIcon fa fa-plus fa-1g');
            } else {
                this.span.innerHTML = this.model.get('button_text');
                this.span.setAttribute('class', 'lmaddBtn');
            }

            this.div.appendChild(this.input);
            this.div.appendChild(this.span);
            this.el.appendChild(this.div);
            this.ul = document.createElement('ul');
            this.ul.setAttribute('class', 'lmUL');
            this.el.appendChild(this.ul);

            // set initial values
            this.lm_list = [];
            var vals =  this.model.get('value');
            for (var i = 0; i < vals.length; i++){
                this.add_list_element(vals[i]);
            }

            this.listenTo(this.model, 'change:value', this.value_changed, this);
        },

        update: function() {
            return ListManagerView.__super__.update.apply(this);
        },

        events: {
            // List of events and their handlers.
            'change': 'handle_lm_change',
        },

        value_changed: function() {

            // remove the old list
            this.ul.innerHTML = '';

            var vals =  this.model.get('value');
            //console.log('value_changed: ' + vals);
            for (var i = 0; i < vals.length; i++){
                this.add_list_element(vals[i]);
            }
        },

        add_list_element: function(val) {
            if (val === '') {
                return
            }
            var li = document.createElement("li");
            var t = document.createTextNode(val);
            li.setAttribute('class', 'lmValue');
            li.appendChild(t);

            // clear name from input box
            this.input.value = "";

            var span = document.createElement("SPAN");
            var txt = document.createTextNode("\u00D7");
            span.className = "close";
            span.appendChild(txt);
            li.appendChild(span);
            this.ul.appendChild(li);

            var that = this;
            span.onclick = function() {
                var div = this.parentElement;
                div.style.display = "none";
                that.update_lm_list();
            }

        },
        update_lm_list: function() {
            this.lm_list = [];
            var children = this.ul.childNodes;
            for (var i = 0; i < children.length; i++) {
                var item = children[i];
                if (item.style.display != "none") {
                    this.lm_list.push(item.textContent.slice(0,-1));
                }
            }

            this.model.set('value', this.lm_list);
            this.touch();
        },

        handle_lm_change: function(evt) {
            // value added from UI
            // console.log("LM CHANGE", evt.target.value);
            if (this.lm_list.indexOf(evt.target.value) === -1) {
                this.add_list_element(evt.target.value);
                this.update_lm_list();
            }
        },
    });

    // Register the ListManagerView with the widget manager.
    return {
        ListManagerView: ListManagerView
    };
});
"""


class ListManager(widgets.DOMWidget):

    _view_name = Unicode('ListManagerView').tag(sync=True)
    _view_module = Unicode('listmanager').tag(sync=True)
    value = List([]).tag(sync=True)
    button_text = Unicode('Add').tag(sync=True)
    list_text = Unicode('New Value...').tag(sync=True)

    # skipped = List([]).tag(sync=True)
    # multiple = Bool(False).tag(sync=True)
    # maxsize = Int(1024*1024).tag(sync=True)

    def __init__(self, **kwargs):

        display(Javascript(js_template))

        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)

        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)


        width = kwargs.get('width', '100%')
        d = dict(width=width)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))

        self.value = kwargs.get('value', [])

        self.in_cb = False
        self.cb = kwargs.get('cb')
        if self.cb:
            self.observe(self._cb, names='value')


    def _cb(self, change):
        if self.in_cb:
            return
        self.in_cb = True
        self.cb(change['name'], change['new'])
        self.in_cb = False

    def _handle_custom_msg(self, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


    @property
    def visible(self):
        return self.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.layout.visibility = 'visible'
            return
        self.layout.visibility = 'hidden'
