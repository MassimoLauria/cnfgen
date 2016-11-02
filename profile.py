#!/usr/bin/env python
"""
Profile script for CNFgen package
"""

from __future__ import print_function


def cnfgen_call():

    from cnfformula import cnfgen

    cmd = ["cnfgen"] + sys.argv[1:]
    cnfgen(cmd)

if __name__ == '__main__':
    
    import sys
    from cProfile   import run as profile

    if len(sys.argv) <= 1:
        print("Usage: {} <cnfgen_args>".format(sys.argv[0]),file=sys.stderr)
        sys.exit(-1)

    profile('cnfgen_call()',sort='tottime')
    
    
