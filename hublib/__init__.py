from pint import UnitRegistry
ureg = UnitRegistry()
ureg.autoconvert_offset_to_baseunit = True
Q_ = ureg.Quantity

__version__ = "0.9.94"
