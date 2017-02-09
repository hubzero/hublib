from __future__ import print_function
import pytest
import sys
import ipywidgets as widgets
from . import setup_test_comm, teardown_test_comm
import hublib.ui as ui
from collections import Counter


class TestString:

    callbacks = Counter()
    cval = ''

    @staticmethod
    def cb(name, val):
        TestString.callbacks[name] += 1
        TestString.cval = val

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_basic(self):
        x = ui.String(
            name='DevName',
            description="Device name.",
            value='Destiny001',
            width='50%'
        )

        assert x.value == 'Destiny001'

        x.value = 'Destiny002'
        assert x.value == 'Destiny002'

        with pytest.raises(ValueError):
            x.value = None

    def test_callback(self):
        x = ui.String(
            name='DevName',
            description="Device name.",
            value='Destiny001',
            cb=self.cb
        )

        x.value = 'Destiny002'
        assert x.value == 'Destiny002'
        assert TestString.cval == 'Destiny002'
        assert TestString.callbacks['DevName'] == 1

        x.value = 'DestinyXXX'
        assert x.value == 'DestinyXXX'
        assert TestString.cval == 'DestinyXXX'
        assert TestString.callbacks['DevName'] == 2

    def test_disable(self):
        x = ui.String(
            name='DevName',
            description="Device name.",
            value='Destiny001',
            width='50%'
        )

        assert x.disabled is False
        x.disabled = True
        assert x.disabled is True
        x.disabled = False
        assert x.disabled is False
