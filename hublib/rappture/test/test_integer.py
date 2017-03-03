from __future__ import print_function
import pytest
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture
from hublib import ureg, Q_


class TestInteger:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('curve.xml')

    def test_read_value1(self):
        assert self.io['input.integer(points)'].value == 10
        assert self.io['input.integer(points).min'].value == 2
        assert self.io['input.integer(points).max'].value == 1000
        assert self.io['input.integer(points).current'].value == 10
        assert self.io['input.integer(points).default'].value == 10

    def test_read_value2(self):
        self.io['input.integer(points)'] = 25
        self.io['input.integer(points).default'] = 15
        assert self.io['input.integer(points).current'].value == 25
        assert self.io['input.integer(points).default'].value == 15

