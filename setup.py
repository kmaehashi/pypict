#!/usr/bin/env python

import shutil
import subprocess
import sys

from setuptools import setup, Command, Extension
from Cython.Build import cythonize


package_command = False


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
        if package_command:
            subprocess.check_call(['make', '-C', 'pict', 'pict'])
            shutil.copy2('pict/pict', 'pypict/pict')


package_data = {}

if '--package-command' in sys.argv:
    sys.argv.remove('--package-command')
    package_command = True
    package_data = {'pypict': ['pict']}


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
    package_data=package_data,
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
