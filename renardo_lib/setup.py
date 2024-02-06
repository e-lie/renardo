#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo_lib',
    version="0.9.4.dev1",
    description='Python livecoding environment - New fork of FoxDot',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo_lib',
        'renardo_lib.Code',
        'renardo_lib.Custom',
        'renardo_lib.Extensions',
        'renardo_lib.Extensions.VRender',
        'renardo_lib.Extensions.SonicPi',
        'renardo_lib.EspGrid',
        'renardo_lib.Effects',
        'renardo_lib.Patterns',
        'renardo_lib.SCLang',
        'renardo_lib.Settings',
        'renardo_lib.Utils',
        'renardo_lib.ServerManager',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    package_data = {'renardo_lib': ['README.md','demo/**', 'osc/**'],},
    install_requires=[
        'renardo_gatherer>=0.1.3.dev0',
        'midiutil',
    ],
)
