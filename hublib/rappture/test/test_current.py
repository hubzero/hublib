from __future__ import print_function
import pytest
import os, sys
sys.path.insert(0, os.path.abspath('../..'))
import hublib.rappture as rappture
from hublib import ureg, Q_

# Test the automatic copying of default values to
# empty current values when loading an xml file.

class TestCurrent:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('current_test.xml')

    def test_1(self):
        # control case: both in xml file
        assert self.io['input.number(temperature).current'].value == Q_(300, ureg.kelvin)
        assert self.io['input.number(temperature).default'].value == Q_(300, ureg.kelvin)

    def test_2(self):
        # only default is set in control file
        assert self.io['input.number(temperature2).default'].value == Q_(300, ureg.kelvin)
        assert self.io['input.number(temperature2).current'].value == Q_(300, ureg.kelvin)

    def test_3(self):
        # both set. current is different that default
        assert self.io['input.number(temperature3).default'].value == Q_(300, ureg.kelvin)
        assert self.io['input.number(temperature3).current'].value == Q_(222, ureg.degC)

    def test_4(self):
        # Default set. No units
        assert self.io['input.number(temperature4).default'].value == 333
        assert self.io['input.number(temperature4).current'].value == 333

    def test_5(self):
        # default set
        assert self.io['input.number(vsweep).default'].value == Q_(4, ureg.volt)
        assert self.io['input.number(vsweep).current'].value == Q_(4, ureg.volt)



