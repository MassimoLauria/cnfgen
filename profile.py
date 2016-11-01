#!/usr/bin/env python
"""
Profile script for CNFgen package
"""

from cnfformula import cnfgen
from cProfile   import run as profile
import sys

cmd = ["cnfgen"] + sys.argv[1:]

profile('cnfgen('+repr(cmd)+')',sort='tottime')
