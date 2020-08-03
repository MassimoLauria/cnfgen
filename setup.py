#!/usr/bin/env python
"""
Setup script for the CNFgen package
"""

from setuptools import setup, find_packages

from cnfformula.info import info

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'PyPI.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=info['project'],
    version=info['version'],
    description=info['description'],
    author=info['author'],
    author_email=info['author_email'],
    url=info['url'],
    license=info['license'],
    packages=find_packages(".", exclude=["tests"]),
    entry_points={
        'console_scripts':
        ['cnfgen=cnfgen.main:main', 'cnfshuffle=cnfgen.cnfshuffle:main'],
    },
    install_requires=['networkx>=2.0', 'pydot>=1.2.3'],
    python_requires='>=3.4',

    # Package long description in Markdown
    long_description=long_description,
    long_description_content_type='text/markdown')
