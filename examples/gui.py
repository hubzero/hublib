import hublib.ui as ui


"""
A limitation of the current widget set is that we cannot
do labels with tooltips and Math (Latex).  This should
be fixed soon.
"""

e1 = ui.Number(
        name='E1',
        description="Longitudinal Young's Modulus",
        units='GPa',
        min='0 GPa',
        max='500 GPa',
        value='138 GPa'
    )

e2 = ui.Number(
        name='E2',
        description="Transverse Young's Modulus In-Plane",
        units='GPa',
        min='0 GPa',
        max='500 GPa',
        value='14.5 GPa'
    )

nu12 = ui.Number(
        name='nu12',
        description="Major In-Plane Poisson's Ratio",
        min=-1.0,
        max=0.5,
        value=0.21
    )

g12 = ui.Number(
        name='G12',
        description="Major In-Plane Shear Modulus",
        units='GPa',
        min=0,
        max=500,
        value=5.86
    )

alpha1 = ui.Number(
            name='alpha1',
            description="Longitudinal Thermal Expansion Coefficient",
            min=10e-6,
            max=100e-6,
            value=1e-6
    )

alpha2 = ui.Number(
            name='alpha2',
            description="Transverse Thermal Expansion Coefficient",
            min=10e-6,
            max=100e-6,
            value=30e-6
    )

material = ui.Form([e1, e2, nu12, g12, alpha1, alpha2], name='Material')

h0 = ui.Number(
        name='h0',
        description="Lamina Thickness",
        units='m',
        min=0,
        max=10e-3,
        value='0.2286 mm'
    )

theta = ui.String(
        name='theta',
        description='Lamina Angle',
        value='[45, -45, -45, 45]'
    )

layup = ui.Form([h0, theta], name='Layup')

nx = ui.Number(
        name='Nx',
        description="Applied Normal Edge Force in X-Direction",
        units='N/m',
        min=-10000,
        max=10000,
        value=0
    )

ny = ui.Number(
        name='Ny',
        description="Applied Normal Edge Force in Y-Direction",
        units='N/m',
        min='-10000N/m',
        max='10000 N/m',
        value=0
    )

nxy = ui.Number(
        name='Nxy',
        description="Applied Edge Shear Force in XY-Direction",
        units='N/m',
        min=-10000,
        max=10000,
        value=0
    )

mx = ui.Number(
        name='Mx',
        description="Applied Bending Moment about X-Axis",
        units='N',
        min=-10000,
        max=10000,
        value=0
    )

my = ui.Number(
        name='My',
        description="Applied Bending Moment about Y-Axis",
        units='N',
        min=-10000,
        max=10000,
        value=0
    )

mxy = ui.Number(
        name='Mxy',
        description="Applied Twisting Moment",
        units='N',
        min=-10000,
        max=10000,
        value=0
    )

ti = ui.Number(
        name='Ti',
        description='Initial Temperature',
        units='degC',  # Beware: 'C' is coulombs!
        min=-273.15,
        max=500,
        value=0
    )

tf = ui.Number(
        name='Tf',
        description='Final Temperature',
        units='degC',
        min=-273.15,
        max=500,
        value=0
    )

loading = ui.Form([nx, ny, nxy, mx, my, mxy, ti, tf], name='Loading')

complam_menu = ui.Tab([material, layup, loading])
