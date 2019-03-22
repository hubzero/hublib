from .input_types import get_inputs, parse, get_outputs, get_outputs_df, get_output_files
from .rw import save, read, rdisplay, run_simtool, DB

import os

# jupyter_notebook_url is set by AppMode extension

def as_app(path):
    try:
        dirname = os.path.dirname(jupyter_notebook_url).replace('/notebooks/', '/apps/')
        path = os.path.join(dirname, path)
    except:
        pass
    return path


def as_nb(path):
    try:
        dirname = os.path.dirname(jupyter_notebook_url).replace('/apps/', '/notebooks/')
        path = os.path.join(dirname, path)
    except:
        pass
    return path
