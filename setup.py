from __future__ import print_function
from setuptools import setup, find_packages
import io
import os
import sys
from setuptools.command.test import test as TestCommand
import hublib

class PyTest(TestCommand):
    user_options = [("cov=", None, "Run coverage"),
                    ("cov-xml=", None, "Generate junit xml report"),
                    ("cov-html=", None, "Generate junit html report"),
                    ("junitxml=", None, "Generate xml of test results")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.cov_xml = False
        self.cov_html = False
        self.junitxml = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov is not None:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]
            if self.cov_xml:
                self.cov.extend(["--cov-report", "xml"])
            if self.cov_html:
                self.cov.extend(["--cov-report", "html"])
        if self.junitxml is not None:
            self.junitxml = ["--junitxml", self.junitxml]

    def run_tests(self):
        try:
            import pytest
        except:
            raise RuntimeError("py.test is not installed, "
                               "run: pip install pytest")
        params = {"args": self.test_args}
        if self.cov:
            params["args"] += self.cov
        if self.junitxml:
            params["args"] += self.junitxml
        errno = pytest.main(**params)
        sys.exit(errno)

def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx

    class BuildSphinxDocs(BuildDoc):

        def run(self):
            if self.builder == "doctest":
                import sphinx.ext.doctest as doctest
                # Capture the DocTestBuilder class in order to return the total
                # number of failures when exiting
                ref = capture_objs(doctest.DocTestBuilder)
                BuildDoc.run(self)
                errno = ref[-1].total_failures
                sys.exit(errno)
            else:
                BuildDoc.run(self)

    return BuildSphinxDocs


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst', 'CHANGES.rst')

# Additional setup commands
cmdclass = {
    'docs': sphinx_builder(),
    'test': PyTest
}

setup(
    name='hublib',
    version=hublib.__version__,
    url='https://github.com/martin-hunt/hublib',
    license='MIT Software License',
    author='Martin Hunt',
    install_requires=['ipywidgets>5.2'],
    author_email='mmh@purdue.edu',
    description='Python library for HUBzero Jupyter Notebooks',
    long_description=long_description,
    packages=['hublib', 'hublib.uq', 'hublib.ui',
              'hublib.tool', 'hublib.use', 'hublib.rappture'],
    include_package_data=True,
    platforms='any',
    tests_require=['pytest-cov', 'pytest'],
    cmdclass=cmdclass,
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Scientific/Engineering :: Information Analysis"
        ],
)
