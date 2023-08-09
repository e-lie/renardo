#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo_sitter',
    version="0.1.0",
    description='Launcher/config editor for Renardo -- experimental fork of FoxDot as modular library',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo_sitter',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    # package_data = {'FoxDotEditor': ['README.md','img/*','tmp/*'],},
    install_requires=['renardo'],
)