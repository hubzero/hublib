from __future__ import print_function
import pytest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture
from hublib import ureg, Q_


class TestCurve:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('curve.xml')

    def test_read_single(self):
        val = self.io['output.curve(single).component.xy'].value
        expected = np.array([[0.01, 0.990049505363],
                             [1.009, 0.265160421676],
                             [2.008, -0.140760579036],
                             [3.007, -0.247306232561],
                             [4.006, -0.129662618375],
                             [5.005, 0.0480355105893],
                             [6.004, 0.137247325002],
                             [7.003, 0.0939557547102],
                             [8.002, -0.016382854697],
                             [9.001, -0.0911450779658]])
        assert np.allclose(val, expected)

    def test_write_single(self):
        a = np.arange(20).reshape(-1, 2)
        self.io['output.curve(single).component.xy'] = a
        val = self.io['output.curve(single).component.xy'].value
        assert np.allclose(a, val)
        expected = """<xy>0.000000e+00 1.000000e+00
2.000000e+00 3.000000e+00
4.000000e+00 5.000000e+00
6.000000e+00 7.000000e+00
8.000000e+00 9.000000e+00
1.000000e+01 1.100000e+01
1.200000e+01 1.300000e+01
1.400000e+01 1.500000e+01
1.600000e+01 1.700000e+01
1.800000e+01 1.900000e+01
</xy>"""
        val = str(self.io['output.curve(single).component.xy'].xml()).strip()
        assert val == expected

    def test_write_single_tuple(self):
        a = np.arange(20).reshape(-1, 2) * 3
        x = a[:, 0]
        y = a[:, 1]
        self.io['output.curve(single).component.xy'] = (x, y)
        val = self.io['output.curve(single).component.xy'].value
        assert np.allclose(x, val[:, 0])
        assert np.allclose(y, val[:, 1])

    def test_write_single_list(self):
        a = np.arange(20).reshape(-1, 2) * 4
        x = a[:, 0]
        y = a[:, 1]
        self.io['output.curve(single).component.xy'] = [x, y]
        val = self.io['output.curve(single).component.xy'].value
        assert np.allclose(x, val[:, 0])
        assert np.allclose(y, val[:, 1])

