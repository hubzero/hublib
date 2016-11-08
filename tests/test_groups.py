from __future__ import print_function
import pytest
import sys
import ipywidgets as widgets
from . import setup_test_comm, teardown_test_comm
import hublib.ui as ui


class TestForm:

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_form(self):

        wlist = []
        for i in range(4):
            wlist.append(ui.String(name='Name%s' % i, description='', value='Description of #%s' % i))

        f = ui.Form(wlist, name='My Form')

        assert f.disabled is False
        for w in wlist:
            assert w.disabled is False

        f.disabled = True
        assert f.disabled is True
        for w in wlist:
            assert w.disabled is True

        f.disabled = False
        assert f.disabled is False
        for w in wlist:
            assert w.disabled is False


class TestTab:

    @classmethod
    def setup_class(cls):
        setup_test_comm()

    @classmethod
    def teardown_class(cls):
        teardown_test_comm()

    def test_form(self):

        wlist = []
        for i in range(4):
            wlist.append(ui.String(name='Name%s' % i, description='', value='Description of #%s' % i))

        f = ui.Tab(wlist)

        assert f.disabled is False
        for w in wlist:
            assert w.disabled is False

        f.disabled = True
        assert f.disabled is True
        for w in wlist:
            assert w.disabled is True

        f.disabled = False
        assert f.disabled is False
        for w in wlist:
            assert w.disabled is False



