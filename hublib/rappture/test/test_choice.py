from __future__ import print_function
import pytest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture
from hublib import ureg, Q_


class TestChoice:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('choice.xml')

    def test_read_value(self):
        val = self.io['input.choice(stats)'].value
        assert val == 'Fermi'
        val = self.io['input.choice(stats).default'].value
        assert val == 'Boltzmann'

    def test_write_value(self):
        self.io['input.choice(stats)'] = 'FooBar'
        val = self.io['input.choice(stats)'].value
        assert val == 'FooBar'
