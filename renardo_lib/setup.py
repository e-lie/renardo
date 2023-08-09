#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo',
    version="0.9.0",
    description='Python livecoding environment - New fork of FoxDot',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo',
        'renardo.lib.Code',
        'renardo.lib.Custom',
        'renardo.lib.Extensions',
        'renardo.lib.Extensions.VRender',
        'renardo.lib.Extensions.SonicPi',
        'renardo.lib.EspGrid',
        'renardo.lib.Effects',
        'renardo.lib.Patterns',
        'renardo.lib.SCLang',
        'renardo.lib.Settings',
        'renardo.lib.Utils'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    # package_data = {'FoxDotEditor': ['README.md','img/*','tmp/*'],},
    # install_requires=['renardo'],
)