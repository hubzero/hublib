hublib
======

hublib is a Python library for the `HUBzero`_ science gateway platform.  It is designed
to be used with  `Jupyter`_ notebooks on the hubs.  Hubs running the Jupyter service
include HUBzero and `nanoHUB`_.  Other hubs will be supported soon.

hublib contains three modules:

* hublib.ui - Makes it easy to create a simple GUI for scientific code in a Jupyter notebook.  Built
  on top of `ipywidgets`_ and `pint`_.
* hublib.tool - Convenience functions for controlling and running tools on the hubs.
* hublib.uq - Simplified interface and GUI components for uncertainty quantification.

The complete documentation is hosted at http://hublib.readthedocs.io.

.. _HUBzero: https://hubzero.org/
.. _nanoHUB: https://nanohub.org/
.. _Jupyter: http://jupyter.org/
.. _ipywidgets: https://github.com/ipython/ipywidgets
.. _pint: https://pint.readthedocs.io/
