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
            dirname = os.path.abspath(dirname)

        xml = os.path.abspath(xml)
        if not os.path.isfile(xml):
            raise ValueError("tool must be a toolname or path to a tool.xml file.")

        sessdir = os.environ['SESSIONDIR']
        invoke_file = os.path.join(dirname, 'middleware', 'invoke')
        if os.path.isfile(invoke_file):
            self.invoke_file = invoke_file
        else:
            self.invoke_file = os.path.join(sessdir, 'invoke_%s' % os.getpid())
            with open(self.invoke_file, 'w') as f:
                print('#!/bin/sh', file=f)
                print('/usr/bin/invoke_app -T %s -C rappture' % dirname, file=f)
            subprocess.call('chmod +x %s' % self.invoke_file, shell=True)

        self.tmp_name = os.path.join(sessdir, 'tool_driver_%s.xml' % os.getpid())
        self.run_name = ""
        self.toolparameters_name = os.path.join(sessdir, 'driver_%s.hz' % os.getpid())
        self.rappturestatus_name = os.path.join(sessdir, 'rappture.status')
        self.dirname = dirname
        self.tool = xml
        RapXML.__init__(self, xml)

    def run(self, verbose=True):
        # print("Writing", self.tmp_name)
        with open(self.tmp_name, 'w') as f:
            f.write(str(self.xml(pretty=False, header=True)))

        with open(self.toolparameters_name, 'w') as f:
            f.write("file(execute):%s" % (self.tmp_name))
        cmd = "TOOL_PARAMETERS=%s %s" % (self.toolparameters_name, self.invoke_file)

        if verbose:
            print("cmd=", cmd)

        cwd = os.getcwd()
        os.chdir(os.environ['SESSIONDIR'])
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

        with(open(self.rappturestatus_name, 'r')) as f:
            statusData = f.readlines()

        for record in statusData:
            if 'output saved in' in record:
                self.run_name = record.strip().split()[-1]
                break

        if self.run_name:
            self.tree = ET.parse(self.run_name)

        os.chdir(cwd)
