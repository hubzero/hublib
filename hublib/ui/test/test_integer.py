from __future__ import print_function
import pytest
import sys
import ipywidgets as widgets
from . import setup_test_comm, teardown_test_comm
import hublib.ui as ui

def setup():
    setup_test_comm()

def teardown():
    teardown_test_comm()

class TestInteger:

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_val(self):
        x = ui.Integer(
            name='XX',
            description='Mystery Parameter',
            min=0,
            max=10,
            value=5
        )
        assert x.value == 5
        assert x.str == '5'

        x.value = '7'
        assert x.value == 7
        assert x.str == '7'

        x.value = 0
        assert x.value == 0
        assert x.str == '0'

        with pytest.raises(ValueError):
            x.value = 0.2

        with pytest.raises(ValueError):
            x.value = '5 m'

        with pytest.raises(ValueError):
            x.value = None


    def test_val_no_minmax(self):
        # Integer without units
        x = ui.Integer(
            name='XX',
            description='Mystery Parameter',
            value=5
        )
        x.value = 50000
        assert x.value == 50000
        assert x.str == '50000'

        x.value = -4000000000000
        assert x.value == -4000000000000
        assert x.str == '-4000000000000'

        # try some bad values
        with pytest.raises(ValueError):
            x.value = '4 m'
        with pytest.raises(ValueError):
            x.value = 'foo'
        with pytest.raises(ValueError):
            x.value = None


    def test_val_min(self):
        x = ui.Integer(
            name='XX',
            description='Mystery Parameter',
            min=1,
            max=10,
            value=8
        )

        with pytest.raises(ValueError):
            x.value = 0

        with pytest.raises(ValueError):
            x.value = -1

    def test_val_max(self):
        x = ui.Integer(
            name='XX',
            description='Mystery Parameter',
            min=1,
            max=10,
            value=8
        )

        with pytest.raises(ValueError):
            x.value = 11

        x.value = 10
        assert x.value == 10

    def test_disable(self):
        x = ui.Integer(
            name='XX',
            description='Mystery Parameter',
            min=5,
            max=10,
            value=8
        )

        assert x.disabled is False
        x.disabled = True
        assert x.disabled is True
        x.disabled = False
        assert x.disabled is False
