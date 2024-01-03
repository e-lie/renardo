#!/usr/bin/env python

from setuptools import setup

# with open("README.md", "r") as f:
#     long_description=f.read()

setup(
    name='renardo_samples_manager',
    version="0.1.0",
    description='Samples manager for Renardo Python livecoding environment',
    author='Elie Gavoty',
    author_email='eliegavoty@free.fr',
    license='cc-by-sa-4.0',
    url='http://renardo.org/',
    packages=[
        'renardo_samples_manager',
    ],
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # entry_points={'gui_scripts' : ['FoxDotEditor = FoxDotEditor.__init__:main']},
    # data_files=[('', 'LICENSE')],
    # package_data = {'renardo_lib': ['README.md','demo/**', 'osc/**'],},
    install_requires=['requests', 'beautifulsoup4'],
    entry_points={
        'console_scripts': [
            'renardo_samples_manager = renardo_samples_manager:main',
        ]
    }
)