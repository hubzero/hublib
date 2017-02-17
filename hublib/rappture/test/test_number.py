from __future__ import print_function
import pytest
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture
from hublib import ureg, Q_


class TestNumber:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('number.xml')

    def test_input_list(self):
        inputs = str(self.io.inputs())
        expected = """input.number(temperature)\t"Ambient temperature"
input.number(temperature2)\t"Ambient Temperature Celsius"
input.number(temperature3)\t"Ambient Temperature Current No Units"
input.number(temperature4)\t"Ambient Temperature Unitless"
input.number(vsweep)\t"Voltage Sweep +/-"
"""

        assert expected == inputs

    def test_output_list(self):
        outputs = str(self.io.outputs())
        expected = """output.number(outt)\t"Ambient temperature"
output.number(outv)\t"Voltage Sweep +/-"
"""
        assert expected == outputs

    def test_read_value1(self):
        val = self.io['input.number(temperature)'].value
        assert val.m == 300
        assert val.u == ureg.kelvin
        assert '{:~}'.format(val) == '300 K'
        assert self.io['input.number(temperature)'].rvalue == '300K'

    def test_read_value2(self):
        val = self.io['input.number(temperature2)'].value
        assert np.isclose(val.m, 26.85)
        assert val.u == ureg.degC
        assert self.io['input.number(temperature2)'].rvalue == '300K'
        assert self.io['input.number(temperature2).units'].rvalue == 'C'

    def test_read_value3(self):
        val = self.io['input.number(temperature3)'].value
        assert val.m == 300
        assert val.u == ureg.degC
        assert '{:~}'.format(val) == '300 celsius'

        assert self.io['input.number(temperature3)'].rvalue == '300'
        assert self.io['input.number(temperature3).units'].rvalue == 'C'

    def test_read_value4(self):
        assert self.io['input.number(temperature4)'].value == 300.0
        assert self.io['input.number(temperature4)'].rvalue == '300'

    def test_write_value1(self):
        # set without units
        self.io['input.number(temperature)'] = 270
        val = self.io['input.number(temperature)'].value
        assert val.m == 270
        assert val.u == ureg.kelvin

    def test_write_value1b(self):
        # set with units
        self.io['input.number(temperature)'] = "260 K"
        val = self.io['input.number(temperature)'].value
        assert val.m == 260
        assert val.u == ureg.kelvin

    def test_write_value1c(self):
        # Set default and check that current is not affected
        self.io['input.number(temperature).default'] = "305 K"
        val = self.io['input.number(temperature).default'].value
        assert val.m == 305
        assert val.u == ureg.kelvin
        val = self.io['input.number(temperature)'].value
        assert val.m == 260
        assert val.u == ureg.kelvin

    def test_write_value2(self):
        # set without units
        self.io['input.number(temperature2)'] = 270
        val = self.io['input.number(temperature2)'].value
        assert val.m == 270
        assert val.u == ureg.degC

    def test_write_value2b(self):
        # set without units
        self.io['input.number(temperature2)'] = "270 K"
        val = self.io['input.number(temperature2)'].value
        assert np.allclose(val.m, -3.15)
        assert val.u == ureg.degC

    def test_write_value2c(self):
        # change units
        self.io['input.number(temperature2).units'] = 'K'
        val = self.io['input.number(temperature2)'].value
        assert val.m == 270
        assert val.u == ureg.kelvin

    def test_write_value4(self):
        # set without units
        self.io['input.number(temperature4)'] = 270
        val = self.io['input.number(temperature4)'].value
        assert val == 270

    def test_write_value4b(self):
        # set without units
        self.io['input.number(temperature4)'] = '270'
        val = self.io['input.number(temperature4)'].value
        assert val == 270

