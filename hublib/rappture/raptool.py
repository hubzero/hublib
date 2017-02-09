from pyxml import Node
from library import library
import subprocess
import os
import sys

"""
The Rappture Tool class is used by python programs
to run Rappture tools.
"""

class Tool(Node):
    def __init__(self, tool):
        """
        tool can be any of the following:

        - Path to a tool.xml file.
        - Name of a published tool.  The current version will be run.

        """
        dirname, xml = os.path.split(tool)
        if dirname == "":
            if xml != "tool.xml":
                # must be tool name
                dirname = "/apps/%s/current" % xml
                xml = dirname + "/rappture/tool.xml"
            else:
                dirname = os.getcwd()
        else:
            xml = tool
            dirname = os.path.abspath(os.path.join(dirname, '..'))

        if not os.path.isfile(xml):
            raise ValueError("tool must ba a toolname or path to a tool.xml file.")

        self.bin = os.path.join(dirname, 'bin')
        if not os.path.isdir(self.bin):
            self.bin = ""

        sessdir = os.path.join(os.environ['HOME'], 'data/sessions', os.environ['SESSION'])
        self.tmp_name = os.path.join(sessdir, 'tool_driver_%s.xml' % os.getpid())
        self.run_name = os.path.join(sessdir, 'tool_run_%s.xml' % os.getpid())
        self.tool_file = xml
        self.lib = library(xml)
        self.path = ''

    def run(self):
        with open(self.tmp_name, 'w') as f:
            f.write(self.xml())

        if self.bin:
            cmd = "PATH=%s:$PATH /apps/bin/rappture -execute %s -tool %s > %s" % \
                (self.bin, self.tmp_name, self.tool_file, self.run_name)
        else:
            cmd = "/apps/bin/rappture -execute %s -tool %s > %s" % (self.tmp_name, self.tool_file, self.run_name)

        try:
            ret = subprocess.call(cmd, shell=True)
            if ret:
                print >>sys.stderr, 'Error: "%s"' % cmd
                if ret < 0:
                    print >>sys.stderr, "Terminated by signal", -ret
                else:
                    print >>sys.stderr, "Returncode", ret
        except OSError as e:
            print >>sys.stderr, 'Error: "%s"' % cmd
            print >>sys.stderr, "Failed:", e
            sys.exit(1)

        self.lib = library(self.run_name)
