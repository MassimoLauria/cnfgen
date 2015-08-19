#!/usr/bin/env python
"""
Setup script for the CNFgen package
"""

from setuptools import setup, find_packages


setup(name='CNFgen',
      version='0.5.4.4',
      description='CNF formula generator',
      author='Massimo Lauria',
      author_email='lauria.massimo@gmail.com',
      url='https://massimolauria.github.io/cnfgen',
      # url='https://github.com/MassimoLauria/cnfgen',
      packages = find_packages(".", exclude=["*.tests"]),
      license='GPL-3',
      entry_points={
          'console_scripts': [
              'cnfgen=cnfformula.cnfgen:command_line_utility',
              'cnfshuffle=cnfformula.utils.cnfshuffle:command_line_utility',
              'cnftransform=cnfformula.utils.dimacstransform:command_line_utility'],
      },
      install_requires=['networkx','pyparsing'],
      # make some tests
      test_suite='nose.collector',
      tests_require=['nose']
     )
