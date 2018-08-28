#!/usr/bin/env python
"""
Setup script for the CNFgen package
"""

from setuptools import setup, find_packages

import cnfformula.prjdata as p

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
            'cnfgen=cnfformula.cnfgen:command_line_utility',
            'cnfshuffle=cnfformula.utils.cnfshuffle:command_line_utility',
            'cnftransform=cnfformula.utils.dimacstransform:command_line_utility'],
    },
    install_requires=['networkx>=1.9,<2.0','pydotplus'],
    # make some tests
    test_suite='nose.collector',
    tests_require=['nose'],
    # only for python 2
    python_requires='>=2.7,<3.0'
)
