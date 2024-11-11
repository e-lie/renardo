#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='renardo_lib',
    version="0.9.13",
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
        'renardo_lib.Extensions.SonicPiSynthDefImporter',
        'renardo_lib.Patterns',
        'renardo_lib.SynthDefManagement',
        'renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings',
        'renardo_lib.Settings',
        'renardo_lib.Utils',
        'renardo_lib.ServerManager',
        'renardo_lib.runtime',
        'renardo_lib.runtime.synthdefs_initialisation',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    package_data = {'renardo_lib': ['README.md','demo/**', 'SynthDefManagement/sclang_code/**'],},
    install_requires=[
        'renardo_gatherer==0.1.4.dev1',
        'midiutil',
    ],
)
