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
        subprocess.check_call(['make', '-C', 'pict', 'clean'])
        subprocess.check_call(['make', '-C', 'pict', 'libpict.so'])
        subprocess.check_call(['make', '-C', 'pict', 'pict'])


with open('pypict/_version.py') as f:
    exec(f.read())

setup(
    name='pypict',
    version=__version__,  # NOQA
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
    python_requires='>=3.7',
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
    package_data={
        'pypict': ['py.typed', 'capi.pyi'],
    },
    cmdclass={
        'build_pict': BuildPictCommand
    },
)
