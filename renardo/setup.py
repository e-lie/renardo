#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo',
    version="1.0.0.dev6",
    description='Launcher/config editor for Renardo livecoding environment',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo',
        'renardo.widgets',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    package_data = {'renardo': ['RenardoTUI.tcss'],},
    install_requires=[
        'renardo-lib==1.0.0.dev6',
        'FoxDotEditor==1.0.0.dev6',
        'renardo_gatherer==0.1.3',
        'psutil',
        'textual',
    ],
    entry_points={
        'console_scripts': [
            'renardo = renardo:entrypoint',
        ]
    }
)