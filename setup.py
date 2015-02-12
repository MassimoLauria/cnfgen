#!/usr/bin/env python
"""
Setup script for the CNFgen package
"""


from setuptools import setup

setup(name='CNFgen',
      version='0.5.1',
      description='CNF formula generator',
      author='Massimo Lauria',
      author_email='lauria@kth.se',
      url='https://github.com/MassimoLauria/cnfgen',
      packages =['cnfformula'],
      license = 'GPL-3',
      entry_points = {
          'console_scripts': ['cnfgen=cnfformula.cnfgen:command_line_utility'],
      },
      install_requires=[
          'networkx',
      ]
     )
