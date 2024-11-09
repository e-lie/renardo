#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description=f.read()

setup(
    name='FoxDotEditor',
    version="0.9.13.dev6",
    description='Original FoxDot editor extracted from FoxDot Project - Live coding music with SuperCollider',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://foxdot.org/',
    packages=['FoxDotEditor'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={'gui_scripts': ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    package_data={'FoxDotEditor': ['README.md', 'img/*', 'tmp/*'], },
    install_requires=[
        'renardo-lib==0.9.13.dev6',
        'renardo_gatherer==0.1.4.dev1',
        'psutil',
        'ttkbootstrap==1.10.1',
    ],
)
