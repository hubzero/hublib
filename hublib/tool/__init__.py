from mendeleev import element
from .. import ureg
from papermill.iorw import load_notebook_node
import papermill as pm
import yaml
import os
import shutil


def run_simtool(nb, outname, inputs, outdir=None, append=True, parallel=False):
    inputs = _get_dict(inputs)
    if outdir is not None:
        if append:
            if not os.path.exists(outdir):
                os.makedirs(outdir)
        else:
            if os.path.exists(outdir):
                shutil.rmtree(outdir)
            os.makedirs(outdir)
    
    pm.execute_notebook(nb, os.path.join(outdir, outname), parameters=inputs)

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

# a javascript-like object. Access using object syntax or as a dictionary
class AttrDict(dict):
    def __init__(self, **kwargs):
        super(AttrDict, self).__init__()
        self.__dict__ = self
        self.desc = kwargs.get('desc')

    def __repr__(self):
        res = []
        for i in self:
            if i == 'desc':
                continue
            res.append('%s:' % i)
            res.append(self[i].__repr__())
        return '\n'.join(res)

def parse(inputs):
    d = AttrDict()
    for i in inputs:
        t = inputs[i]['type']
        if t == 'Text':
            d[i] = Text(**inputs[i])
        elif t == 'Element':
            d[i] = Element(**inputs[i])
        elif t == 'Integer':
            d[i] = Integer(**inputs[i])
        elif t == 'Number':
            d[i] = Number(**inputs[i])
    return d

def set_variables(inputs):
    for i in inputs:
        val = inputs[i]['value']
        globals()[i] = val

def _get_dict(inputs):
    if type(inputs) == dict:
        return inputs
    d = {}
    for i in inputs:
        try:
            d[i] = inputs[i].value
        except:
            pass
    # return {'inputs': d}
    return d

class Integer(AttrDict):
    def __init__(self, value, **kwargs):
        super(Integer, self).__init__(**kwargs)
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.value = value

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
        res = '    value: %s\n' % self.value
        for i in self:
            if not i.startswith('_') and self[i] is not None:
                res += '    %s: %s\n' % (i, self[i])
        return res


class Text(AttrDict):
    def __init__(self, value, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.value = value
        self.options = kwargs.get('options')
        self.maxlen = kwargs.get('maxlen')

    def __repr__(self):
        res = ''
        for i in self:
            if self[i] is not None:
                res += '    %s: %s\n' % (i, self[i])
        return res

class Element(AttrDict):
    def __init__(self, value, property, **kwargs):
        super(Element, self).__init__(**kwargs)
        self.property = property
        self.value = value
        self.options = kwargs.get('options')

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, newval):
        if type(newval) is str:
            self._e = element(newval.title())
        else:
            self._e = element(newval)
        self._value = self._e.__dict__[self.property]

    def __repr__(self):
        res = '    value: %s\n' % self.value
        for i in self:
            if not i.startswith('_') and self[i] is not None:
                res += '    %s: %s\n' % (i, self[i])
        return res

class Number(AttrDict):
    def __init__(self, value, *args, **kwargs):
        super(Number, self).__init__()
        self.min = kwargs.get('min')
        if self.min is not None:
            self.min = float(self.min)
        self.max = kwargs.get('max')
        if self.max is not None:
            self.max = float(self.max)

        units = kwargs.get('units')
        if units:
            try:
                self.units = ureg.parse_units(units)
            except:
                raise ValueError('Unrecognized units: %s' % units)
        self.value = value

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
        res = '    value: %s\n' % self.value
        for i in self:
            if not i.startswith('_') and self[i] is not None:
                res += '    %s: %s\n' % (i, self[i])
        return res
