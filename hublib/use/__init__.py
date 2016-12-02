import sys
import os
from IPython.core.magic import register_line_magic


"""
Line magic to allow the 'use' command to load environment modules.
This works on the current environment, so we cannot simply fork a shell.
Maybe some trick to fork a shell and return the modified environment would work?
For now lets see how this works.  Just implement "setenv", "prepend", and "use".
Works for all currently installed modules except two old ones that use local shell variables.
"""

EPATH = '/apps/share64/debian7/environ.d'


def setenv(line):
    # print 'SETENV', line
    name, val = line
    os.environ[name] = val


def prepend(line):
    # print 'PREPEND', line
    name, val = line
    try:
        oldval = os.environ[name]
        val = '%s:%s' % (val, oldval)
    except:
        pass
    os.environ[name] = val


def _use(name):
    fname = os.path.join(EPATH, name)

    with open(fname) as fp:
        for line in fp:
            line = line.strip().split()
            if line == []:
                continue
            if line[0] == 'prepend':
                prepend(line[1:])
                continue
            if line[0] == 'setenv':
                setenv(line[1:])
                continue
            if line[0] == 'use':
                _use(line[-1])


@register_line_magic
def use(name):
    _use(name)

# We delete this to avoid name conflicts for automagic to work
del use
