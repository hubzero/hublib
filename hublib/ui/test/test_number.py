from __future__ import print_function
import pytest
import sys
import ipywidgets as widgets

#-----------------------------------------------------------------------------
# Utility stuff
#-----------------------------------------------------------------------------

from . import setup_test_comm, teardown_test_comm
import hublib.ui as ui


def setup():
    setup_test_comm()


def teardown():
    teardown_test_comm()


class TestNumber:

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_val(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=0,
            max=10,
            value='5 m'
        )
        assert x.value == 5
        assert x.str == '5 m'

        x.value = '7.1 m'
        assert x.value == 7.1
        assert x.str == '7.1 m'

        x.value = 0.2
        assert x.value == 0.2
        assert x.str == '0.2 m'

    def test_val2(self):
        # initial value has no units
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=0,
            max=10,
            value=5
        )
        assert x.value == 5
        assert x.str == '5 m'

        x.value = '7.1 m'
        assert x.value == 7.1
        assert x.str == '7.1 m'

        x.value = '0.2'
        assert x.value == 0.2
        assert x.str == '0.2 m'

    def test_val_unitless(self):
        # Number without units
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            min=0,
            max=10,
            value=5
        )
        assert x.value == 5
        assert x.str == '5'

        # simulate pressing enter
        x.cb('')
        assert x.value == 5
        assert x.str == '5'

        x.value = 4.4
        assert x.value == 4.4
        assert x.str == '4.4'

        x.cb('')
        assert x.value == 4.4
        assert x.str == '4.4'

        # try some bad values
        with pytest.raises(ValueError):
            x.value = '4 m'
        with pytest.raises(ValueError):
            x.value = 'foo'
        with pytest.raises(ValueError):
            x.value = None

    def test_val_no_minmax(self):
        # Number without units
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            value=5
        )
        x.value = 50000
        assert x.value == 50000
        assert x.str == '50000'

        x.value = -400000
        assert x.value == -400000
        assert x.str == '-400000'

        # try some bad values
        with pytest.raises(ValueError):
            x.value = '4 m'
        with pytest.raises(ValueError):
            x.value = 'foo'
        with pytest.raises(ValueError):
            x.value = None

    def test_val_convert(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=0,
            max=10,
            value='5 m'
        )

        x.value = '10 cm'
        assert x.value == 0.1
        assert x.str == '0.1 m'

    def test_val_min(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=5,
            max=10,
            value=8
        )

        with pytest.raises(ValueError):
            x.value = 1

        with pytest.raises(ValueError):
            x.value = '1 m'

        # 500 cm = 5 m, so OK
        x.value = '500 cm'
        assert x.value == 5

        # 499 cm NOT OK
        with pytest.raises(ValueError):
            x.value = '499 cm'

    def test_val_max(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=5,
            max=10,
            value=8
        )

        with pytest.raises(ValueError):
            x.value = 10.001

        with pytest.raises(ValueError):
            x.value = '11 m'

        # 1000 cm = 10 m, so OK
        x.value = '1000 cm'
        assert x.value == 10

        # 1001 cm NOT OK
        with pytest.raises(ValueError):
            x.value = '1001 cm'

    def test_change_minmax(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=5,
            max=10,
            value=8
        )

        assert x.min == 5
        assert x.max == 10

        x.min = 1
        assert x.min == 1

        x.max = 100
        assert x.max == 100

    def test_disable(self):
        x = ui.Number(
            name='XX',
            desc='Mystery Parameter',
            units='m',
            min=5,
            max=10,
            value=8
        )

        assert x.disabled is False
        x.disabled = True
        assert x.disabled is True
        x.disabled = False
        assert x.disabled is False
