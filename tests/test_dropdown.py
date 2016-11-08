from __future__ import print_function
import pytest
import sys
import ipywidgets as widgets
from . import setup_test_comm, teardown_test_comm
import hublib.ui as ui


class TestDropDown:

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_basic(self):
        x = ui.Dropdown(
            name='Nut',
            description="Type of nut to put on the sundae.",
            options=['Walnuts', 'Pecans', 'Almonds'],
            value='Walnuts',
            width='50%'
        )

        assert x.value == 'Walnuts'

        x.value = 'Almonds'
        assert x.value == 'Almonds'

        with pytest.raises(ValueError):
            x.value = 'Peanuts'

        with pytest.raises(ValueError):
            x.value = None

    def test_dict(self):
        x = ui.Dropdown(
            name='Nut',
            description="Type of nut to put on the sundae.",
            options={'Walnuts': 1, 'Pecans': 2, 'Almonds': 3},
            value=1,
            width='50%'
        )

        assert x.value == 1

        x.value = 2
        assert x.value == 2

        with pytest.raises(ValueError):
            x.value = 'Walnuts'

        with pytest.raises(ValueError):
            x.value = 4

        with pytest.raises(ValueError):
            x.value = None

    def test_disable(self):
        x = ui.Dropdown(
            name='Nut',
            description="Type of nut to put on the sundae.",
            options=['Walnuts', 'Pecans', 'Almonds'],
            value='Walnuts',
            width='50%'
        )
        assert x.disabled is False
        x.disabled = True
        assert x.disabled is True
        x.disabled = False
        assert x.disabled is False
