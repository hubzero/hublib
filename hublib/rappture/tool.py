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

        sessdir = os.path.join(os.environ['SESSIONDIR'], str(os.getpid()))
        subprocess.call('mkdir -p %s' % sessdir, shell=True)

        invoke_file = os.path.join(dirname, 'middleware', 'invoke')
        if os.path.isfile(invoke_file):
            self.invoke_file = invoke_file
        else:
            self.invoke_file = os.path.join(sessdir, 'invoke')
            with open(self.invoke_file, 'w') as f:
                print('#!/bin/sh -l', file=f)
                print('/usr/bin/invoke_app "$@" -T %s -C rappture' % (dirname), file=f)
            subprocess.call('chmod +x %s' % self.invoke_file, shell=True)

        self.driver_name = os.path.join(sessdir, 'tool_driver.xml')
        self.toolparameters_name = os.path.join(sessdir, 'driver.hz')
        self.rappturestatus_name = os.path.join(sessdir, 'rappture.status')
        self.dirname = dirname
        self.sessdir = sessdir
        self.tool = xml
        RapXML.__init__(self, xml)

    def run(self, verbose=False):
        with open(self.driver_name, 'w') as f:
            f.write(str(self.xml(pretty=False, header=True)))

        with open(self.toolparameters_name, 'w') as f:
            f.write("file(execute):%s" % (self.driver_name))
        cmd = "/bin/sh -l -c \"TOOL_PARAMETERS=%s %s -d %s\"" % (self.toolparameters_name, self.invoke_file, self.sessdir)

        if verbose:
            print(cmd)

        cwd = os.getcwd()
        os.chdir(os.path.join(os.environ['SESSIONDIR'], str(os.getpid())))

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

        run_name = None
        for record in statusData:
            if 'output saved in' in record:
                run_name = record.strip().split()[-1]
                break

        if run_name is not None:
            self.tree = ET.parse(run_name)

        os.chdir(cwd)
        self.reload()

