#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo',
    version="0.9.3.dev0",
    description='Launcher/config editor for Renardo -- experimental fork of FoxDot as modular library',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    # package_data = {'FoxDotEditor': ['README.md','img/*','tmp/*'],},
    install_requires=[
        'renardo-lib>=0.9.2',
        'FoxDotEditor>=0.9.2',
        'psutil',
        'textual',
    ],
    entry_points={
        'console_scripts': [
            'renardo = renardo:entrypoint',
        ]
    }
)