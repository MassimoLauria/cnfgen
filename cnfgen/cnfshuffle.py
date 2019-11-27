#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Cnf formulas shuffling."""


import os
import sys
import random
import argparse

from cnfformula import readCNF
from cnfformula import Shuffle

from .cmdline import paginate_or_redirect_stdout
from .cmdline import redirect_stdin
from .cmdline import interactive_msg
from .cmdline import error_msg
from .cmdline import setup_SIGINT


def command_line_utility(argv=sys.argv):

    # Parse the command line arguments
    progname = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=progname,
                                     description="""
    Reshuffle the input CNF. Returns a formula logically
    equivalent to the input with random application of
    (1) Polarity flips (2) Variables permutation (3) Clauses permutation.
    """,
                                     epilog="""
    For more information type '%s [--help | -h ]'
    """ % (progname))

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
    parser.add_argument('--seed', '-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument('--input', '-i',
                        type=argparse.FileType('r'),
                        metavar="<input>",
                        default='-',
                        help="""Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)
    parser.add_argument('--no-polarity-flips', '-p',
                        action='store_true',
                        dest='no_polarity_flips',
                        help="No polarity flips")
    parser.add_argument('--no-variables-permutation', '-v',
                        action='store_true',
                        dest='no_variable_permutations',
                        help="No permutation of variables")
    parser.add_argument('--no-clauses-permutation', '-c',
                        action='store_true',
                        dest='no_clause_permutations',
                        help="No permutation of clauses")
    parser.add_argument('--quiet', '-q',
                        action='store_false',
                        default=True,
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    # Process the options
    args = parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args, 'seed') and args.seed:
        random.seed(args.seed)

    msg = """Waiting for a DIMACS formula on <stdin>.
             Alternatively you can feed a formula to <stdin>
             with piping or using '-i' command line argument."""

    try:

        with redirect_stdin(args.input):
            interactive_msg(msg, 'c INPUT: ')
            input_cnf = readCNF()

    except ValueError as parsefail:
        error_msg(str(parsefail), 'c DIMACS PARSE ERROR: ')
        sys.exit(-1)

    # Default permutation
    if not args.no_variable_permutations:
        variable_permutation = None
    else:
        variable_permutation = list(input_cnf.variables())

    if not args.no_clause_permutations:
        clause_permutation = None
    else:
        clause_permutation = list(range(len(input_cnf)))

    if not args.no_polarity_flips:
        polarity_flip = None
    else:
        polarity_flip = [1]*len(list(input_cnf.variables()))

    output_cnf = Shuffle(input_cnf,
                         variable_permutation,
                         clause_permutation,
                         polarity_flip)

    with paginate_or_redirect_stdout(args.output):
        output_cnf._dimacs_dump_clauses(output=sys.stdout,
                                        export_header=args.verbose)


# Launcher
if __name__ == '__main__':
    setup_SIGINT()
    command_line_utility(sys.argv)
