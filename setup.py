#!/usr/bin/env python

import shutil
import subprocess
import sys

from setuptools import setup, Command, Extension
from Cython.Build import cythonize


class BuildPictCommand(Command):

    description = 'build PICT shared library'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call(['make', '-C', 'pict', 'clean'])
        subprocess.check_call(['make', '-C', 'pict', 'libpict.so'])


with open('pypict/_version.py') as f:
    exec(f.read())

setup(
    name='pypict',
    version=__version__,
    description='pypict: Python binding for Microsoft PICT',
    long_description=open('README.rst').read(),
    author='Kenichi Maehashi',
    author_email='webmaster@kenichimaehashi.com',
    url='https://github.com/kmaehashi/pypict',
    license='MIT License',
    packages=[
        'pypict',
    ],
    test_suite='tests',
    python_requires='>=3.6.0',
    ext_modules=cythonize(
        Extension(
            'pypict.capi',
            ['pypict/capi.pyx'],
            include_dirs=['pict/api'],
            library_dirs=['pict'],
            libraries=['pict'],
        ),
        language_level=3,
    ),
    cmdclass={
        'build_pict': BuildPictCommand
    },
)
