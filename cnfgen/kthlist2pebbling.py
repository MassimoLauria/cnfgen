#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to build dimacs encoding of pebbling formulas

Accepts only the kthlist graph format:

ASSUMPTIONS: the graph is given with a line for each vertex, from
sources to a *single sink*.

CNF formulas interesting for proof complexity.
"""

import os
import sys
import argparse

from cnfformula import PebblingFormula
from cnfformula import readGraph

from .cmdline import paginate_or_redirect_stdout
from .cmdline import redirect_stdin
from .msg import interactive_msg
from .msg import error_msg
from .cmdline import setup_SIGINT

from .msg import interactive_msg
from .msg import error_msg
from .msg import msg_prefix

#################################################################
#          Command line tool follows
#################################################################


# Command line helpers
def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
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
    parser.add_argument('--input', '-i',
                        type=argparse.FileType('r'),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
    parser.add_argument('--quiet', '-q',
                        action='store_false',
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    # Cmdline parser for formula transformations
    from cnfformula import transformations
    from cnfformula.cmdline import is_transformation_helper
    from cnfformula.cmdline import find_methods_in_package

    transformation_helpers = find_methods_in_package(
        transformations,
        is_transformation_helper,
        sortkey=lambda x: x.name)

    
    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")
    for sc in transformation_helpers:
        p = subparsers.add_parser(sc.name,
                                  help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)


# Main program
def command_line_utility(argv=sys.argv):

    # Parse the command line arguments
    parser = argparse.ArgumentParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)
    args = parser.parse_args(argv[1:])

    ask_kthlist_graph = """
       Waiting for a directed acyclic graph on <stdin>,
       in 'kthlist' format.

       See: https://massimolauria.net/cnfgen/graphformats.html"""

    with redirect_stdin(args.input), msg_prefix('c '):

        with msg_prefix('GRAPH INPUT: '):
            interactive_msg(ask_kthlist_graph)

        try:
            G = readGraph(sys.stdin, "dag", file_format="kthlist")
        except ValueError as parsefail:
            with msg_prefix('KTHLIST ERROR: '):
                error_msg(str(parsefail))
            sys.exit(-1)

    F = PebblingFormula(G)

    if hasattr(args, "transformation"):
        F2 = args.transformation.transform_cnf(F, args)
    else:
        F2 = F

    with paginate_or_redirect_stdout(args.output):
        print(F2.dimacs(export_header=args.verbose))


# Launcher
if __name__ == '__main__':
    setup_SIGINT()
    command_line_utility(sys.argv)
