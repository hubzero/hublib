from __future__ import print_function
import pytest
import os, sys

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture


class TestLog:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('log.xml')

    def test_log(self):
        val = self.io['output.log'].value
        expected = "This is a log message."
        assert val == expected

    def test_log2(self):
        val = self.io['output.log(output_log)'].value
        expected = "This is another log message."
        assert val == expected

    def test_log3(self):
        log = self.io['output.log(output_log)']
        assert log['about/label'].value == "Output Log"

