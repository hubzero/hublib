UI Module
=========

.. module:: hublib.ui

Widget Groups
-------------

Tab
***

.. class:: Tab(wlist, [titles=None])

    Creates a tabbed dialog containing *wlist*, the list of widgets.  The name of each widget
    will appear in the tabs.

    :param wlist: A list of widgets that make up the form.

    :param titles:  An optional list of titles for the tabs.  If None, the names of
        the widgets in *wlist* will be used.

    Attributes:

    .. attribute:: disabled

        Set to True to disable all the contained widgets.

    >>> f = ui.Tab([form1, form2])


Form
****

.. class:: Form(wlist, [name="", desc="", disabled=False, width=None])

    A form is a vertically-stacked list of widgets grouped together.

    :param wlist: A list of widgets that make up the form.

    :param name: The name of the form.  Will appear in a tab or label if the form is put in
        another Form or Tab.

    :param desc: An optional description that will appear in a popover dialog.

    :param disabled: The initial state of the form. Defaults to False.

    :param width: Optional width of the form as a percent string (for example, '50%').
        Default is None which sets the width automatically to contain all the
        widgets.

    Attributes:


    .. attribute:: desc

        The form description.

    .. attribute:: disabled

        Set to True to disable all the contained widgets.

    .. attribute:: name

        The form name.

    .. attribute:: visible

        Set to False to hide the form.

    .. attribute:: width

        The form width.


    >>> f = ui.Form([checkbox1, checkbox2, num1, string1], name="My Parameters")


Numerical Widgets
-----------------

Number
******

.. class:: Number(name, value, [cb=None, desc='', disabled=False, units=None, width='auto', min=None, max=None])

    A text field that contains a floating point number with optional units and optional minimum and maximum. Units are converted and min and max checked dynamically.

    :param name: The name that will appear in the field.
    :param value: The initial value.
    :param cb: An optional callback function.
    :param desc: An optional description. This will appear in a popover dialog along with
        unit and min and max values when available.
    :param disabled: The initial state of the form. Defaults to False.
    :param units: A string containing an abbreviation or full name for the unit of measurement.
    :param width: Optional width of the form as a percent string (for example, '50%').
        Default sets the width automatically to contain all the widgets.
    :param min:
    :param max:  Minimum and maximum values.  If a string, may contain units.  Otherwise units will be assumed to
        be the same as those set by the units parameter.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: desc

    .. attribute:: disabled

        Set to True to disable the widget.

    .. attribute:: max

    .. attribute:: min

    .. attribute:: name

    .. attribute:: str

        Read-only.  The value as a string, including units.  For example "5.2 m"

    .. attribute:: value

        When read, the value expressed as a floating point number.

        When writing, you can set the value to any expression that can be converted to the proper
        units.  Bad units or values outside the permitted min/max values will cause an exception.

    .. attribute:: visible

        Set to False to hide the widget.

    .. attribute:: width


    >>> e1 = ui.Number(
        name='E1',
        description="Longitudinal Young's Modulus",
        units='GPa',
        min=0,
        max=500,
        value='138 GPa',
        width='20%'
    )

.. image::  images/number.gif

Integer
*******

.. class:: Integer(name, value, [cb=None, desc='', disabled=False, width='auto', min=None, max=None])

    A text field that contains an integer with optional minimum and maximum. Min and max are checked dynamically.

    :param name: The name that will appear in the field.
    :param value: The initial value.
    :param cb: An optional callback function.
    :param desc: An optional description. This will appear in a popover dialog along with
        min and max values when available.
    :param disabled: The initial state of the form. Defaults to False.
    :param width: Optional width of the form as a percent string (for example, '50%').
        Default sets the width automatically to contain all the widgets.
    :param min:
    :param max:  Minimum and maximum values.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: desc

    .. attribute:: disabled

        Set to True to disable the widget.

    .. attribute:: max

    .. attribute:: min

    .. attribute:: name

    .. attribute:: str

        Read-only.  The value as a string, including units.  For example "5.2 m"

    .. attribute:: value

        When read, the integer value.

        When writing, values outside the permitted min/max values will cause an exception.

    .. attribute:: visible

        Set to False to hide the widget.

    .. attribute:: width

    >>> loops = ui.Integer(
        name='Loops',
        description="Number of Loops to Run",
        min=0,
        max=500,
        value=12,
        width='20%'
    )

    .. image::  images/integer.png


Input Widgets
-------------

Checkbox
***********

.. class:: Checkbox(name, desc, value, [cb=None, disabled=False, width='auto'])


    >>> check = ui.Checkbox('Advanced Options', 'Show the Advanced Options', value=False, width='50%')
    print check.value
    False

Radiobuttons
************

.. class:: Radiobuttons(name, desc, options, value, [cb=None, disabled=False, width='auto'])

    >>> r = ui.Radiobuttons(
            name='Nut',
            description="Type of nut to eat.",
            value='almond',
            options=['peanut', 'walnut', 'almond', 'pecan'],
            width='20%'
        )
    print r.value
    'almond'

Dropdown
********

.. class:: Dropdown(name, desc, options, value, [cb=None, disabled=False, width='auto'])

    Creates a dropdown or pulldown widget.

    :param name: The name that will appear in the field.
    :param desc: An optional description. This will appear in a popover dialog.
    :param options: A list of strings or dictionay of strings with values.
    :param value: The initial value.
    :param cb: An optional callback function.
    :param disabled: The initial state of the form. Defaults to False.
    :param width: Optional width of the form as a percent string (for example, '50%').
        Default sets the width automatically to contain all the widgets.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: disabled

        Set to True to disable the widget.

    .. attribute:: value

    .. attribute:: visible

        Set to False to hide the widget.

    .. attribute:: width

    >>> tb = ui.Dropdown(
            name='Nut',
            description="Type of nut to eat.",
            value='almond',
            options=['peanut', 'walnut', 'almond', 'pecan'],
            width='20%'
        )
    >>> tb.value
    'almond'

    or using a dictionary:

    >>> tb = ui.Dropdown(
            name='Nut',
            description="Type of nut to eat.",
            value=2,
            options={'peanut':1, 'walnut':2, 'almond':3, 'pecan':4},
            width='20%'
        )
    >>> tb.value
    2

    .. image::  images/dropdown.png

Togglebuttons
*************

.. class:: Togglebuttons(name, desc, options, value, [cb=None, disabled=False, width='auto'])

    Creates a horizontal bar of buttons.  Only one can be selected.

    :param name: The name that will appear in the field.
    :param desc: An optional description. This will appear in a popover dialog.
    :param options: A list of strings or dictionay of strings with values.
    :param value: The initial value.
    :param cb: An optional callback function.
    :param disabled: The initial state of the form. Defaults to False.
    :param width: Optional width of the form as a percent string (for example, '50%').
        Default sets the width automatically to contain all the widgets.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: disabled

        Set to True to disable the widget.

    .. attribute:: value

    .. attribute:: visible

        Set to False to hide the widget.

    .. attribute:: width

    >>> tb = ui.Togglebuttons(
            name='Nut',
            description="Type of nut to eat.",
            value='almond',
            options=['peanut', 'walnut', 'almond', 'pecan'],
            width='20%'
        )
    >>> tb.value
    'almond'

    or using a dictionary:

    >>> tb = ui.Togglebuttons(
            name='Nut',
            description="Type of nut to eat.",
            value=2,
            options={'peanut':1, 'walnut':2, 'almond':3, 'pecan':4},
            width='20%'
        )
    >>> tb.value
    2

    .. image::  images/togglebuttons.png

String
***********

.. class:: String(name, desc, value='', [cb=None, disabled=False, width='auto'])

    A single-line text input box.

    >>> xstr = ui.String(name="Name", description='Name (First and Last)', value='<name>')
    >>> print xstr.value
    <name>

Text
***********

.. class:: Text(name, desc, value='', [cb=None, disabled=False, width='auto'])

    A multi-line text input box.

    >>> xtxt = ui.Text(name="Description",
                       description='Experiment Description',
                       value='Starting Content')
    >>> print xtxt.value
    Starting Content


Download
--------

.. class:: Download(filename, **kwargs)

    A button that downloads a remote file to the browser.

    :param filename: The file that will be downloaded.
    :param label: The label on the button. Default is the filename.
    :param icon: Optional icon name. Must be from http://fontawesome.io/icons/
    :param tooltip: An optional tooltip.
    :param style: Default is ''. Supported values are "success", "info", "warning", and "danger".
    :param cb: Optional callback function.


File Upload
-----------

.. class:: FileUpload(name, desc, options, [width='auto'])

    A button that opens a file browser on your computer that allows you to upload a single or multiple files.
    Data will be downloaded when the *save* method is called.

    :param name: The name that will appear in the field.
    :param desc: An optional description. This will appear in a popover dialog.
    :param disabled: The initial state. Defaults to False.
    :param cb: An optional callback function called when the upload completes.
    :param width: Optional width as a percent string (for example, '50%').
    :param multiple: Allow multiple files to be selected. Default False.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: visible

        Set to False to hide the widget.

    .. image::  images/fileupload.png

    list(sizes=False)
        Returns a list of filenames with optional sizes.

        >>> f.list()
        ['quote1.txt', 'quote2.txt']
        >>> f.list(sizes=True)
        [('quote1.txt', 94), ('quote2.txt', 186)]

    save(name=None, dir=None)
        Uploads the files.

        If **name** is a string and only a single file is selected, the file will be uploaded
        to that name. If **dir** is a string, a directory with that name will be created
        (if necessary) and the file(s) will be placed there.

Modal
--------

.. class:: Modal(**kwargs)

    A simple modal dialog.

    :param body: The text for the dialog body.
    :param title: The title for the dialog.
    :param buttons: A list of button labels.
    :param primary: The name or the index of the default button.  It will be highlighted.
    :param cb: Optional callback function.

    >>> def modal_callback(val):
        print("Modal Dialog Returned", val)

    >>> Modal(body="This is a test modal dialog.",
      title='TEST DIALOG',
      icon='fa-bell',
      buttons=['CANCEL', 'OK'],
      cb=modal_callback)


ListManager
-----------

.. class:: ListManager(value=[], button_text='Add', list_text='New Value...')

    A list manager widget. Allows adding and removing items from a list.

    :param body: The text for the dialog body.
    :param title: The title for the dialog.
    :param buttons: A list of button labels.
    :param primary: The name or the index of the default button.  It will be highlighted.
    :param cb: Optional callback function.

    Attributes:
        Attributes are parameters that may be modified or read after the object is created.
        Unless noted, attributes are read/write.

    .. attribute:: value

        Sets or gets the values in the widgets's list.

    .. attribute:: visible

        Set to False to hide the widget.

    .. attribute:: width

    >>> initial_list = ['Hydrogen', 'Helium', 'Lithium']
    >>> lm = ListManager(value = initial_list, list_text='Element..', button_text='', cb=LMCB)
    >>> print(lm.value)
    ['Hydrogen', 'Helium', 'Lithium']

    .. image::  images/listmanager.gif

RunAllButton
------------

.. class:: RunAllButton(label='Run All Cells', icon='', tooltip='', style='', cb=None, hide=False)

    A button that runs all the code cells.

    :param label: The text for button.
    :param icon: Optional icon name. Must be from http://fontawesome.io/icons/
    :param tooltip: optional tooltip.
    :param style: Default is ''. Supported values are "success", "info", "warning", and "danger".
    :param cb: Optional callback function.
    :param hide: If True, hide code cells.


HideCodeButton
--------------

.. class:: HideCodeButton(label, icon='', tooltip='', style='', cb=None)

    A button that hides all the code cells.

    :param label: The text for button. It can be a string or a list of two strings.
        The default is ['Hide Code Cells', 'Show Code Cells']
    :param icon: Optional icon name. Must be from http://fontawesome.io/icons/
    :param tooltip: optional tooltip.
    :param style: Default is ''. Supported values are "success", "info", "warning", and "danger".
    :param cb: Optional callback function.


PathSelector
------------

.. autoclass:: PathSelector
   :members: visible, disabled

RunCommand
----------

.. autoclass:: RunCommand
   :members: run


Submit
------

.. autoclass:: Submit
   :members: run

   .. method:: make_rname(*args)

    Creates a unique directory name given a variable number
    of input arguments.

   :returns: A long string which is guaranteed to be a unique
    directory in ``~/data/results/.submit_cache/${cachename}``

Submit() can cache results.  If *cachename* is not None, it must
be a unique name for the tool or notebook.  A user 
directory will be created for storing results in ``~/data/results/.submit_cache/${cachename}``  Each run will need a unique name, *runname*.  The developer is responsible for generating this.  For
very simple cases, the runs can be simply named, like "run1", or "volt5cap6".  However, submit requires alphanumeric characters only, so no dashes, underscores or  periods.  This makes naming challenging.  To assist with this, Submit includes a handy method, make_rname().  make_rname() takes a variable number or args of any type and produces a unique runname.  

For more information, see the example notebooks.

