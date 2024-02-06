#!/usr/bin/env python

from setuptools import setup

setup(
    name='renardo_gatherer',
    version="0.1.3.dev1",
    description='Asset collector for Renardo Python livecoding environment',
    long_description="""
    Asset collector (samples packs, synthdefs, etc) for Renardo Python livecoding environment
    """,
    long_description_content_type="text/markdown",
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo_gatherer',
    ],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'indexed',
    ],
    entry_points={
        'console_scripts': [
            'renardo_gatherer = renardo_gatherer:main',
        ]
    }
)