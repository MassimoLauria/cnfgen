#!/usr/bin/env python
"""
Profile script for CNFgen package
"""

import os
import sys
from cProfile import run
from cnfgen.clitools.cmdline import paginate_or_redirect_stdout


def cnfgen_call():
    from cnfgen import cnfgen

    cmd = ["cnfgen"] + sys.argv[1:]

    with open(os.devnull, "w") as null:
        old_stdout = sys.stdout
        sys.stdout = null

        cnfgen(cmd)

        sys.stdout = old_stdout


def main():
    if len(sys.argv) <= 1:
        print("Usage: {} <cnfgen_args>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(-1)

    with paginate_or_redirect_stdout(sys.stdout):
        run('cnfgen_call()', sort='tottime')


if __name__ == '__main__':
    main()
