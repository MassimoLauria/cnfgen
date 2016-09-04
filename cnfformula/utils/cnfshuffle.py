#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Cnf formulas shuffling."""

from __future__ import print_function

import os


import sys
import random
from .. import CNF
from .  import dimacs2cnf

from ..transformations.shuffle import Shuffle


def command_line_utility(argv=sys.argv):

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
        print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
        print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
        print(" * http://code.google.com/p/argparse",file=sys.stderr)
        print("",file=sys.stderr)
        exit(-1)

    # Parse the command line arguments
    progname=os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=progname,
                                     description="""
    Reshuffle the input CNF. Returns a formula logically
    equivalent to the input with random application of
    (1) Polarity flips (2) Variables permutation (3) Clauses permutation.
    """,
                                     epilog="""
    For more information type '%s [--help | -h ]'
    """ % (progname))

    parser.add_argument('--output','-o',
                        type=argparse.FileType('wb',0),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)
    parser.add_argument('--seed','-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)
    parser.add_argument('--no-polarity-flips','-p',action='store_true',dest='no_polarity_flips',help="No polarity flips")
    parser.add_argument('--no-variables-permutation','-v',action='store_true',dest='no_variable_permutations',help="No permutation of variables")
    parser.add_argument('--no-clauses-permutation','-c',action='store_true',dest='no_clause_permutations',help="No permutation of clauses")

    parser.add_argument('--quiet', '-q',action='store_false',default=True,dest='verbose',
                        help="""Output just the formula with no header.""")


    # Process the options
    args=parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    input_cnf = dimacs2cnf(args.input)
    output_cnf = Shuffle(input_cnf,
                         variable_permutation=None if not args.no_variable_permutations else list(input_cnf.variables()),
                         clause_permutation=None if not args.no_clause_permutations else range(len(input_cnf)),
                         polarity_flip=None if not args.no_polarity_flips else [1]*len(list(input_cnf.variables())))
    output_cnf._dimacs_dump_clauses(output=args.output,
                                    export_header=args.verbose)

    if args.output != sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)

