from __future__ import print_function
from .node import Node
import numpy as np
from lxml import etree as ET
import os
from subprocess import call, Popen, PIPE
import sys
from .rappture import RapXML
from hublib.use import _use


def get_info(tname):
    modlist = []

    with open(tname) as f:
        inv = get_invoke_line(f)

    if inv == "" or inv is None:
        return None, None

    prog = 'rappture'
    args = iter(inv.split())
    for arg in args:
        if arg == '-C':
            prog = next(args)
        if arg == '-u':
            modlist.append(next(args))
    return prog, modlist

def get_invoke_line(f):
    line = ""
    for newline in f:
        if newline.rstrip().endswith('\\'):
            line += newline.rstrip()[:-1]
            continue
        line += newline
        if len(line.split()) == 0:
            continue
        first = line.split()[0]
        if first.endswith('invoke_app'):
            return line
        line = ""


class Tool(RapXML):
    def __init__(self, tool):
        """
        tool can be any of the following:

        - Path to a tool.xml file.
        - Name of a published tool.  The current version will be run.

        """
        dirname, toolname = os.path.split(tool)
        if dirname == "":
            if toolname != "tool.xml":
                # must be tool name
                dirname = "/apps/%s/current" % toolname
                toolname = dirname + "/rappture/tool.xml"
            else:
                dirname = os.getcwd()
        else:
            toolname = tool
            dirname = os.path.abspath(os.path.join(dirname, '..'))

        toolname = os.path.abspath(toolname)
        if not os.path.isfile(toolname):
            raise ValueError("tool must be a toolname or path to a tool.xml file.")

        self.bin = os.path.join(dirname, 'bin')
        if not os.path.isdir(self.bin):
            self.bin = ""

        invoke_file = os.path.join(dirname, 'middleware', 'invoke')
        if os.path.isfile(invoke_file):
            prog, modules = get_info(invoke_file)
            # print("prog=%s, modules=%s" % (prog, modules))
            if prog != 'rappture':
                raise ValueError("Tool does not appear to be a Rappture tool.")

            for m in modules:
                _use(m)

        sessdir = os.environ['SESSIONDIR']
        self.tmp_name = os.path.join(sessdir, 'tool_driver_%s.xml' % os.getpid())
        self.run_name = os.path.join(sessdir, 'tool_run_%s.xml' % os.getpid())
        self.dirname = dirname
        self.tool = toolname
        RapXML.__init__(self, toolname)


    def run(self, verbose=False):
        # print("Writing", self.tmp_name)
        with open(self.tmp_name, 'w') as f:
            f.write(str(self.xml(pretty=True, header=True)))

        if self.bin:
            cmd = "PATH=%s:$PATH /apps/bin/rappture -execute %s -tool %s > %s" % \
                (self.bin, self.tmp_name, self.tool, self.run_name)
        else:
            cmd = "/apps/bin/rappture -execute %s -tool %s > %s" % \
                (self.tmp_name, self.tool, self.run_name)

        cwd = os.getcwd()
        os.chdir(os.environ['SESSIONDIR'])
        failed = False

        if verbose:
            print("cmd=", cmd)
            try:
                p1 = Popen(cmd, shell=True, stderr=PIPE)
                print(p1.communicate()[1])
                ret = p1.returncode
            except OSError as e:
                failed = e
        else:
            try:
                ret = call(cmd, shell=True)
            except OSError as e:
                failed = e

        if failed:
            print('Error: "%s"' % cmd, file=sys.stderr)
            print("Failed:", failed, file=sys.stderr)
            sys.exit(1)

        if ret:
            print('Error: "%s"' % cmd, file=sys.stderr)
            if ret < 0:
                print("Terminated by signal", -ret, file=sys.stderr)
            else:
                print("Returncode", ret, file=sys.stderr)
        os.chdir(cwd)
        self.tree = ET.parse(self.run_name)
