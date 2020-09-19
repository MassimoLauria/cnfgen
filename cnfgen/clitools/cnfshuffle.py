#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Cnf formulas shuffling."""

import os
import sys
import random
import argparse

from cnfgen.utils.parsedimacs import readCNF
from cnfgen.transformations.shuffle import Shuffle

from cnfgen.clitools.cmdline import paginate_or_redirect_stdout
from cnfgen.clitools.cmdline import redirect_stdin
from cnfgen.clitools.cmdline import setup_SIGINT
from cnfgen.clitools.cmdline import CLIParser, CLIError

from cnfgen.clitools.msg import interactive_msg
from cnfgen.clitools.msg import error_msg
from cnfgen.clitools.msg import msg_prefix
from cnfgen.clitools.msg import InternalBug


def cli(argv=sys.argv, mode='output'):
    """CNFgen shuffler

    This function provide the main interface to cnfshuffle.


    Parameters
    ----------
    argv: list, optional
        The list of token with the command line arguments/options.

    mode: str
        One among 'formula', 'string', 'output' (latter is the default)
        - 'formula' return a CNF object
        - 'string' return the string with the output of CNFgen
        - 'output' output the formula to the user
    """

    # Parse the command line arguments
    progname = os.path.basename(argv[0])
    parser = CLIParser(prog=progname,
                       description="""
    Reshuffle the input CNF. Returns a formula logically
    equivalent to the input with random application of
    (1) Polarity flips (2) Variables permutation (3) Clauses permutation.
    """,
                       epilog="""
    For more information type '%s [--help | -h ]'
    """ % (progname))

    parser.add_argument('--output',
                        '-o',
                        type=argparse.FileType('w'),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)
    parser.add_argument('--seed',
                        '-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument(
        '--input',
        '-i',
        type=argparse.FileType('r'),
        metavar="<input>",
        default='-',
        help=
        """Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)
    parser.add_argument('--no-polarity-flips',
                        '-p',
                        action='store_true',
                        dest='no_polarity_flips',
                        help="No polarity flips")
    parser.add_argument('--no-variables-permutation',
                        '-v',
                        action='store_true',
                        dest='no_variable_permutations',
                        help="No permutation of variables")
    parser.add_argument('--no-clauses-permutation',
                        '-c',
                        action='store_true',
                        dest='no_clause_permutations',
                        help="No permutation of clauses")
    parser.add_argument('--quiet',
                        '-q',
                        action='store_false',
                        default=True,
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    # Be lenient on non string arguments
    argv = [str(x) for x in argv]

    # Process the options
    args = parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args, 'seed') and args.seed:
        random.seed(args.seed)

    msg = """Waiting for a DIMACS formula on <stdin>.
             Alternatively you can feed a formula to <stdin>
             with piping or using '-i' command line argument."""

    with redirect_stdin(args.input), msg_prefix('c '):
        with msg_prefix("INPUT: "):
            interactive_msg(msg, filltext=70)

        F = readCNF()

    # Default permutation
    if not args.no_variable_permutations:
        variable_permutation = None
    else:
        variable_permutation = list(F.variables())

    if not args.no_clause_permutations:
        clause_permutation = None
    else:
        clause_permutation = list(range(len(F)))

    if not args.no_polarity_flips:
        polarity_flip = None
    else:
        polarity_flip = [1] * len(list(F.variables()))

    G = Shuffle(F, variable_permutation, clause_permutation, polarity_flip)

    if mode == 'formula':
        return G
    elif mode == 'string':
        return G.dimacs(export_header=args.verbose)
    else:
        with paginate_or_redirect_stdout(args.output):
            G._dimacs_dump_clauses(output=sys.stdout,
                                   export_header=args.verbose)


# Launcher
def main():
    setup_SIGINT()

    try:

        cli(sys.argv)

    except ValueError as e:
        error_msg("DIMACS ERROR: " + str(e))
        sys.exit(-1)

    except CLIError as e:
        error_msg(str(e))
        sys.exit(-1)

    except InternalBug as e:
        print(str(e), file=sys.stderr)
        sys.exit(-1)

    except (BrokenPipeError, IOError):
        # avoid errors when stdout is closed before the end of the
        # program (i.e. piping into a command line which does
        # not work.)
        pass

    # avoid signaling BrokenPipeError as whatnot
    sys.stderr.close()


if __name__ == '__main__':
    main()
