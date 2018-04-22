#!/usr/bin/env python

import subprocess

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
        subprocess.check_call(['make', '-C', 'pict', 'libpict.so'])


with open('pypict/_version.py') as f:
    exec(f.read())

setup(
    name='pypict',
    version=__version__,
    description='pypict: Python binding for Microsoft PICT',
    author='Kenichi Maehashi',
    author_email='webmaster@kenichimaehashi.com',
    url='https://github.com/kmaehashi/pypict',
    license='MIT License',
    packages=[
        'pypict',
    ],
    test_suite='tests',
    ext_modules=cythonize(
        Extension(
            'pypict.capi',
            ['pypict/capi.pyx'],
            include_dirs=['pict/api'],
            library_dirs=['pict'],
            libraries=['pict'],
        )
    ),
    cmdclass={
        'build_pict': BuildPictCommand
    },
)
