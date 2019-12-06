#!/usr/bin/env python
"""
Setup script for the CNFgen package
"""

from setuptools import setup, find_packages

import cnfformula.prjdata as p

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'PyPI.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name         = p.__project_name__,
    version      = p.__version__,
    description  = p.__project_description__,
    author       = p.__author__,
    author_email = p.__author_email__,
    url          = p.__url__,
    license      = p.__license__,
    packages     = find_packages(".", exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'cnfgen=cnfgen.main:command_line_utility',
            'cnfshuffle=cnfgen.cnfshuffle:command_line_utility',
            'cnftransform=cnfgen.cnftransform:command_line_utility'],
    },
    install_requires=['networkx>=2.0', 'pydot>=1.2.3'],
    python_requires='>=3.4',

    # Package long description in Markdown
    long_description=long_description,
    long_description_content_type='text/markdown'
)
