Introduction
============

hublib is a Python library for the `HUBzero`_ science gateway platform.  It is designed
to be used with  `Jupyter`_ notebooks on the hubs.  Hubs running the Jupyter service
include HUBzero and `nanoHUB`_.  Other hubs will be supported soon.

hublib contains four modules:

* hublib.ui - Makes it easy to create a simple GUI for scientific code in a Jupyter notebook.  Built
  on top of `ipywidgets`_ and `pint`_.
* hublib.rappture - Compatibility library for running and interacting with `Rappture`_
  tools on the hubs.
* hublib.tool - Convenience functions for controlling and running tools on the hubs.
* hublib.use - Loads hub environment modules.
* hublib.uq - (Future) Simplified interface and GUI components for uncertainty quantification.

.. image::  images/hublib_complam.gif

.. image::  images/hublib_2.gif

.. image::  images/hublib_3.gif

.. _HUBzero: https://hubzero.org/
.. _nanoHUB: https://nanohub.org/
.. _Jupyter: http://jupyter.org/
.. _ipywidgets: https://github.com/ipython/ipywidgets
.. _pint: https://pint.readthedocs.io/
.. _Rappture: https://nanohub.org/infrastructure/rappture
