from __future__ import print_function
from setuptools import setup, find_packages
import io
import os
import sys

import hublib
print(hublib.__version__)

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst', 'CHANGES.rst')


setup(
    name='hublib',
    version=hublib.__version__,
    url='https://github.com/martin-hunt/hublib',
    license='MIT Software License',
    author='Martin Hunt',
    install_requires=['ipywidgets>5.2'
                    ],
    author_email='mmh@purdue.edu',
    description='Python library for HUBzero Jupyter Notebooks',
    long_description=long_description,
    packages=['hublib', 'hublib.uq'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Scientific/Engineering :: Information Analysis"
        ],
)
