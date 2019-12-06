#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF transformation, it increases the hardness of a CNF.

This is the implementation of a command line utility that transform
CNF files in DIMACS format into new  CNFs

Utilities to apply to a dimacs CNF file, a transformation which
increase the hardness of the formula

Accept a cnf in dimacs format in input
"""
import os
import sys
import argparse

from cnfformula import readCNF

from .cmdline import paginate_or_redirect_stdout
from .cmdline import redirect_stdin
from .cmdline import setup_SIGINT
from .cmdline import get_transformation_helpers

from .msg import interactive_msg
from .msg import error_msg
from .msg import msg_prefix


def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument('--input', '-i',
                        type=argparse.FileType('r'),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The input formula is read as a dimacs CNF file file
                        instead of standard input. Setting '<input>'
                        to '-' is another way to read from standard
                        input. (default: -) """)

    parser.add_argument('--output', '-o',
                        type=argparse.FileType('w'),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)

    parser.add_argument('--quiet', '-q',
                        action='store_false',
                        default=True,
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    # Cmdline parser for formula transformations
    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")
    
    for sc in get_transformation_helpers():
        p = subparsers.add_parser(sc.name,
                                  help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)


# Main program
def command_line_utility(argv=sys.argv):

    parser = argparse.ArgumentParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)
    args = parser.parse_args(argv[1:])

    msg = """Waiting for a DIMACS formula on <stdin>.
             Alternatively you can feed a formula to <stdin>
             with piping or using '-i' command line argument."""

    with redirect_stdin(args.input), msg_prefix('c '):
        with msg_prefix("INPUT: "):
            interactive_msg(msg, filltext=70)

        try:
            F = readCNF()
        except ValueError as parsefail:
            with msg_prefix('DIMACS ERROR: '):
                error_msg(str(parsefail))
            sys.exit(-1)

    if hasattr(args, "transformation"):
        G = args.transformation.transform_cnf(F, args)
    else:
        G = F

    with paginate_or_redirect_stdout(args.output):
        print(G.dimacs(args.verbose))


# Launcher
if __name__ == '__main__':
    setup_SIGINT()
    command_line_utility(sys.argv)
