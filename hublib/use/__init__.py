"""
Line magic to allow the 'use' command to load hub environment modules.
This works on the current environment, so we cannot simply fork a shell.
Maybe some trick to fork a shell and return the modified environment would work?
For now lets see how this works.  Just implement "setenv", "prepend", and "use".
Works for all currently installed modules except two old ones that use local shell variables.
"""

import sys
import os
from string import Template
from IPython.core.magic import register_line_magic

EPATH = '/apps/share64/debian7/environ.d'
d = {}


def setenv(line):
    name = line[0]
    val = ' '.join(line[1:])
    os.environ[name] = val

def prepend(line):
    global d
    name, val = line
    val = Template(val).safe_substitute(d)
    try:
        oldval = os.environ[name]
        val = '%s:%s' % (val, oldval)
    except:
        pass
    os.environ[name] = val

    if name == 'PYTHONPATH':
        for p in reversed(val.split(':')):
            sys.path.insert(1,p)


def _set(a, b):
    global d
    t = Template(b)
    b = t.safe_substitute(d)
    d[a] = b

def _use(name):
    if not name[0] == '.':
        fname = os.path.join(EPATH, name)

    with open(fname) as fp:
        for line in fp:
            sline = line.strip().split()
            if sline == []:
                continue
            if sline[0] == 'prepend':
                prepend(sline[1:])
                continue
            if sline[0] == 'setenv':
                setenv(sline[1:])
                continue
            if sline[0] == 'use':
                _use(sline[-1])
                continue
            line = line.split("=")
            if len(line) == 2:
                _set(line[0].strip(), line[1].strip())

try:
    get_ipython()

    @register_line_magic
    def use(name):
        _use(name)

    # We delete this to avoid name conflicts for automagic to work
    del use
except:
    pass
