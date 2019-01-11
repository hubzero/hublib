from .. import ureg
from papermill.iorw import load_notebook_node
import papermill as pm
import yaml
import os
import sys
import shutil
import copy
import numpy as np
import json
import plotly
import plotly.graph_objs as go
import IPython
from IPython.display import display as idisplay, Video, Image
from base64 import b64decode, b64encode


# A dictionary-like object that can also
# be accessed by attributes.  Note that you
# cannot access attributes by key, only keys
# can be accessed by attributes.
class Params(object):
    def __init__(self, **kw):
        self.__members = []
        for k in kw:
            self[k] = kw[k]

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        if not key in self.__members:
            self.__members.append(key)

    def has_key(self, key):
        return hasattr(self, key)

    def keys(self):
        return self.__members

    def iterkeys(self):
        return self.__members

    def __iter__(self):
        return iter(self.__members)

    def __repr__(self):
        res = []
        for i in self.__members:
            res.append('%s:' % i)
            res.append(self[i].__repr__())
        return '\n'.join(res)

def get_inputs(nbname):
    incell = None
    nb = load_notebook_node(nbname)
    for cell in nb.cells:
        if cell['source'].startswith('%%yaml INPUTS'):
            incell = cell['source']
            break
    if incell is None:
        return None
    # remove first line (cell magic)
    incell = incell.split('\n', 1)[1]
    input_dict = yaml.load(incell)
    return parse(input_dict)


def parse(inputs):
    d = Params()
    for i in inputs:
        t = inputs[i]['type']
        if t == 'Text':
            d[i] = Text(**inputs[i])
        elif t == 'Integer':
            d[i] = Integer(**inputs[i])
        elif t == 'Number':
            d[i] = Number(**inputs[i])
        elif t == 'List':
            d[i] = List(**inputs[i])
        elif t == 'Dict':
            d[i] = Dict(**inputs[i])
        elif t == 'Array':
            d[i] = Array(**inputs[i])
        else:
            print('Unknown type:', t, file=sys.stderr)
    return d

def set_variables(inputs, scope):
    for i in inputs:
        val = inputs[i].value
        scope[i] = val


class Integer(Params):
    def __init__(self, **kwargs):
        # always set these first
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        super(Integer, self).__init__(**kwargs)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, newval):
        if self.min is not None and newval < self.min:
            raise ValueError("Minimum value is %d" % self.min)
        if self.max is not None and newval > self.max:
            raise ValueError("Maximum value is %d" % self.max)
        self._value = newval
    
    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i])
        return res


class Text(Params):
    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i])
        return res


class List(Params):
    def __init__(self, **kwargs):
        super(List, self).__init__(**kwargs)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i])
        return res


class Dict(Params):
    def __init__(self, **kwargs):
        super(Dict, self).__init__(**kwargs)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i])
        return res

class Array(Params):
    def __init__(self, **kwargs):
        super(Array, self).__init__(**kwargs)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newval):
        if type(newval) is np.ndarray:
            newval = newval.tolist()
        self._value = newval

    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i].__repr__())
        return res

class Number(Params):
    def __init__(self, **kwargs):
        # always set these first
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.units = kwargs.get('units')
        super(Number, self).__init__(**kwargs)
        if self.units:
            try:
                self.units = ureg.parse_units(self.units)
            except:
                raise ValueError('Unrecognized units: %s' % self.units)
        # always put something in for 'value'
        if 'value' not in kwargs:
            self['value'] = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newval):
        if self.units and type(newval) == str:
            newval = ureg.parse_expression(newval)
            if hasattr(newval, 'units'):
                newval = newval.to(self.units).magnitude
        if self.min is not None and newval < self.min:
            raise ValueError("Minimum value is %d" % self.min)
        if self.max is not None and newval > self.max:
            raise ValueError("Maximum value is %d" % self.max)
        self._value = newval

    def __repr__(self):
        res = ''
        for i in self:
            res += '    %s: %s\n' % (i, self[i])
        return res
