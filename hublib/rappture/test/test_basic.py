from __future__ import print_function
import pytest
import os, sys
sys.path.insert(0, os.path.abspath('../..'))
import hublib.rappture as rappture


class TestBasic:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('basic.xml')

    def test_input_list(self):
        inputs = str(self.io.inputs())
        expected = ""
        assert expected == inputs

    def test_output_list(self):
        outputs = str(self.io.outputs())
        expected = ""
        assert expected == outputs

    def test_read_tool_info(self):
        assert self.io['tool.title'].value == 'Name of the tool'
        assert self.io['tool.about'].value == 'Description and credits'
        assert self.io['tool.command'].value == '@tool/path/to/executable @driver'

    def test_write_tool_info(self):
        self.io['tool.title'] = 'New Title'
        assert self.io['tool.title'].value == 'New Title'

    def test_xml_output(self):
        xml = str(self.io.xml())
        print("XML=", xml)
        print()
        expected = """<run>
  <tool>
    <title>New Title</title>
    <about>Description and credits</about>
    <command>@tool/path/to/executable @driver</command>
    <limits>
      <cputime>900</cputime>
    </limits>
    <action><label>Simulate</label></action>
    <layout>xxx</layout>
    <control>xxx</control>
    <uq>true</uq>
    <analyzer>xxx</analyzer>
    <reportJobFailures>1</reportJobFailures>
  </tool>
</run>
"""
        assert xml == expected

    def test_xml_partial_output(self):
        xml = str(self.io['tool.title'].xml()).strip()
        print("XML=", xml)
        print()
        expected = """<title>New Title</title>"""
        assert expected == xml

    def test_escaping(self):
        self.io['tool.title'] = "\"Black&White<'xyzzy'>\""
        assert self.io['tool.title'].value == "\"Black&White<'xyzzy'>\""
        assert self.io['tool.title'].rvalue == "\"Black&White<'xyzzy'>\""

    def test_shortcuts(self):
        tool = self.io['tool']
        tool['title'] = 'My Test Title'
        assert tool['title'].value == 'My Test Title'
        title = tool['title']
        assert title.value == 'My Test Title'
