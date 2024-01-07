#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo_lib',
    version="0.9.1.dev1",
    description='Python livecoding environment - New fork of FoxDot',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo_lib',
        'renardo_lib.lib',
        'renardo_lib.lib.Code',
        'renardo_lib.lib.Custom',
        'renardo_lib.lib.Extensions',
        'renardo_lib.lib.Extensions.VRender',
        'renardo_lib.lib.Extensions.SonicPi',
        'renardo_lib.lib.EspGrid',
        'renardo_lib.lib.Effects',
        'renardo_lib.lib.Patterns',
        'renardo_lib.lib.SCLang',
        'renardo_lib.lib.Settings',
        'renardo_lib.lib.Utils'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    package_data = {'renardo_lib': ['README.md','demo/**', 'osc/**'],},
    install_requires=['renardo_gatherer==0.1.0.dev1'],
)
