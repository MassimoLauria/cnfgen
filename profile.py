#!/usr/bin/env python
"""
Profile script for CNFgen package
"""


import os
import sys
from contextlib import contextmanager

@contextmanager
def erase_stdout():

    with file(os.devnull,"w") as null:
        old_stdout = sys.stdout
        sys.stdout = null

        yield
    
        sys.stdout = old_stdout

def cnfgen_call():

    from cnfformula import cnfgen

    cmd = ["cnfgen"] + sys.argv[1:]

    with erase_stdout():
        cnfgen(cmd)


if __name__ == '__main__':
    
    from cProfile   import run as profile

    if len(sys.argv) <= 1:
        print("Usage: {} <cnfgen_args>".format(sys.argv[0]),file=sys.stderr)
        sys.exit(-1)

    profile('cnfgen_call()',sort='tottime')
    
    
