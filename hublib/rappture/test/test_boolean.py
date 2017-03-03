from __future__ import print_function
import pytest
import os, sys

sys.path.insert(0, os.path.abspath('../../..'))
import hublib.rappture as rappture


class TestBoolean:

    @classmethod
    def setup_class(cls):
        print("cls", cls)
        cls.io = rappture.RapXML('boolean.xml')

    def test_input_rvalues_new(self):
        assert self.io['input.boolean(iimodel)'].rvalue == 'off'
        assert self.io['input.boolean(iimodel1)'].rvalue == 'yes'
        assert self.io['input.boolean(iimodel2)'].rvalue == 'true'
        assert self.io['input.boolean(iimodel3)'].rvalue == '1'

    def test_input_rvalues_old(self):
        assert self.io['input.boolean(iimodel).current'].rvalue == 'off'
        assert self.io['input.boolean(iimodel1).current'].rvalue == 'yes'
        assert self.io['input.boolean(iimodel2).current'].rvalue == 'true'
        assert self.io['input.boolean(iimodel3).current'].rvalue == '1'

    def test_input_rdefaults(self):
        assert self.io['input.boolean(iimodel).default'].rvalue == 'on'
        assert self.io['input.boolean(iimodel1).default'].rvalue == 'yes'
        assert self.io['input.boolean(iimodel2).default'].rvalue == 'true'
        assert self.io['input.boolean(iimodel3).default'].rvalue == '1'

    def test_input_values_new(self):
        assert self.io['input.boolean(iimodel)'].value is False
        assert self.io['input.boolean(iimodel1)'].value is True
        assert self.io['input.boolean(iimodel2)'].value is True
        assert self.io['input.boolean(iimodel3)'].value is True

    def test_input_defaults(self):
        assert self.io['input.boolean(iimodel).default'].value is True
        assert self.io['input.boolean(iimodel1).default'].value is True
        assert self.io['input.boolean(iimodel2).default'].value is True
        assert self.io['input.boolean(iimodel3).default'].value is True

    # now do outputs

    def test_output_rvalues_new(self):
        assert self.io['output.boolean(outb)'].rvalue == 'off'
        assert self.io['output.boolean(outb1)'].rvalue == 'yes'
        assert self.io['output.boolean(outb2)'].rvalue == 'true'
        assert self.io['output.boolean(outb3)'].rvalue == '1'

    def test_output_rvalues_old(self):
        assert self.io['output.boolean(outb).current'].rvalue == 'off'
        assert self.io['output.boolean(outb1).current'].rvalue == 'yes'
        assert self.io['output.boolean(outb2).current'].rvalue == 'true'
        assert self.io['output.boolean(outb3).current'].rvalue == '1'

    def test_output_values_old(self):
        assert self.io['output.boolean(outb).current'].value is False
        assert self.io['output.boolean(outb1).current'].value is True
        assert self.io['output.boolean(outb2).current'].value is True
        assert self.io['output.boolean(outb3).current'].value is True

    def test_output_values_new(self):
        assert self.io['output.boolean(outb)'].value is False
        assert self.io['output.boolean(outb1)'].value is True
        assert self.io['output.boolean(outb2)'].value is True
        assert self.io['output.boolean(outb3)'].value is True

    def test_write_values_new(self):

        # These are recommended
        self.io['output.boolean(outb)'] = True
        self.io['output.boolean(outb1)'] = False

        # These are accepted, but not recommended
        self.io['output.boolean(outb2)'] = 0
        self.io['output.boolean(outb3)'] = 'no'

        assert self.io['output.boolean(outb)'].value is True
        assert self.io['output.boolean(outb1)'].value is False
        assert self.io['output.boolean(outb2)'].value is False
        assert self.io['output.boolean(outb3)'].value is False

    def test_write_values_new2(self):
        self.io['output.boolean(outb)'] = 'false'
        self.io['output.boolean(outb1)'] = 'yes'
        self.io['output.boolean(outb2)'] = 'on'
        self.io['output.boolean(outb3)'] = '1'

        assert self.io['output.boolean(outb)'].value is False
        assert self.io['output.boolean(outb1)'].value is True
        assert self.io['output.boolean(outb2)'].value is True
        assert self.io['output.boolean(outb3)'].value is True

    def test_write_values_current(self):
        self.io['input.boolean(iimodel)'] = True
        self.io['input.boolean(iimodel1)'] = True
        self.io['input.boolean(iimodel2)'] = False
        self.io['input.boolean(iimodel3)'] = False

        assert self.io['input.boolean(iimodel).current'].value == True
        assert self.io['input.boolean(iimodel1).current'].value == True
        assert self.io['input.boolean(iimodel2).current'].value == False
        assert self.io['input.boolean(iimodel3).current'].value == False

    def test_write_values_current2(self):
        self.io['input.boolean(iimodel)'] = False
        self.io['input.boolean(iimodel1)'] = True
        self.io['input.boolean(iimodel2)'] = False
        self.io['input.boolean(iimodel3)'] = True

        assert self.io['input.boolean(iimodel)'].value == False
        assert self.io['input.boolean(iimodel1)'].value == True
        assert self.io['input.boolean(iimodel2)'].value == False
        assert self.io['input.boolean(iimodel3)'].value == True

    def test_write_rvalues_current(self):
        self.io['input.boolean(iimodel)'].rvalue = 'on'
        self.io['input.boolean(iimodel1)'].rvalue = 'true'
        self.io['input.boolean(iimodel2)'].rvalue = 'False'
        self.io['input.boolean(iimodel3)'].rvalue = 'off'
        assert self.io['input.boolean(iimodel).current'].rvalue == 'on'
        assert self.io['input.boolean(iimodel1).current'].rvalue == 'true'
        assert self.io['input.boolean(iimodel2).current'].rvalue == 'False'
        assert self.io['input.boolean(iimodel3).current'].rvalue == 'off'
