Use Module
==========

.. module:: hublib.use

The tool module implements the "line magic" to load
hub environment modules.

On the hubs, the "use" command can load different packages into the current environment.  You can get help and a list of these from a workspace command line by typing "use".

    >>> ~> use
    Syntax: use [-h] [-e|-p] [-k|-r] [-x] <environment>
       -h: help (specify an environment to find out more about it)
       -e: Environment only.  Act on the current shell.  Do not preserve.
       -p: Preserve selection across sessions without prompting.
       -k: Keep an already selected version.
       -r: Replace an already selected version without prompting.
       -x: Print no errors (and take no action) if the environment doesn't exist.

**%use** works the same way in a notebook cell.

    >>> import hublib.use
    %use oommf-1.2b0

