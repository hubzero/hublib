from __future__ import print_function
from .node import Node
import numpy as np
from lxml import etree as ET
import os
import subprocess
import sys
from .rappture import RapXML

class Tool(RapXML):
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
            raise ValueError("tool must be a toolname or path to a tool.xml file.")

        self.bin = os.path.join(dirname, 'bin')
        if not os.path.isdir(self.bin):
            self.bin = ""

        # FIXME; why are run*.xml files created in local directory?
        sessdir = os.path.join(os.environ['HOME'], 'data/sessions', os.environ['SESSION'])
        self.tmp_name = os.path.join(sessdir, 'tool_driver_%s.xml' % os.getpid())
        self.run_name = os.path.join(sessdir, 'tool_run_%s.xml' % os.getpid())
        self.fname = xml
        self.tree = ET.parse(xml)
        self.path = ''


    def run(self):
        print("Writing", self.tmp_name)
        with open(self.tmp_name, 'w') as f:
            f.write(self.xml(pretty=False, header=True))

        if self.bin:
            cmd = "PATH=%s:$PATH /apps/bin/rappture -execute %s -tool %s > %s" % \
                (self.bin, self.tmp_name, self.fname, self.run_name)
        else:
            cmd = "/apps/bin/rappture -execute %s -tool %s > %s" % \
                (self.tmp_name, self.fname, self.run_name)

        print("cmd=", cmd)
        try:
            ret = subprocess.call(cmd, shell=True)
            if ret:
                print('Error: "%s"' % cmd, file=sys.stderr)
                if ret < 0:
                    print("Terminated by signal", -ret, file=sys.stderr)
                else:
                    print("Returncode", ret, file=sys.stderr)
        except OSError as e:
            print('Error: "%s"' % cmd, file=sys.stderr)
            print("Failed:", e, file=sys.stderr)
            sys.exit(1)

        self.tree = ET.parse(self.run_name)
