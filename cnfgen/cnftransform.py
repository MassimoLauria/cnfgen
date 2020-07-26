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
from .cmdline import CLIParser, CLIError

from .msg import interactive_msg
from .msg import error_msg
from .msg import msg_prefix
from .msg import InternalBug


def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument(
        '--input',
        '-i',
        type=argparse.FileType('r'),
        metavar="<input>",
        default='-',
        help="""Input file. The input formula is read as a dimacs CNF file file
                        instead of standard input. Setting '<input>'
                        to '-' is another way to read from standard
                        input. (default: -) """)

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

    parser.add_argument('--quiet',
                        '-q',
                        action='store_false',
                        default=True,
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    # Cmdline parser for formula transformations
    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")

    for sc in get_transformation_helpers():
        p = subparsers.add_parser(sc.name, help=sc.description)
        sc.setup_command_line(p)
        sc.subparser = p
        p.set_defaults(transformation=sc)


# Main program
def command_line_utility(argv=sys.argv, mode='output'):
    """CNFgen transformation to a dimacs input

    This function provide the main interface to cnftransform.

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

    parser = CLIParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)

    # Be lenient on non string arguments
    argv = [str(x) for x in argv]
    print(argv)

    args = parser.parse_args(argv)
    print(args)

    msg = """Waiting for a DIMACS formula on <stdin>.
             Alternatively you can feed a formula to <stdin>
             with piping or using '-i' command line argument."""

    with redirect_stdin(args.input), msg_prefix('c '):
        with msg_prefix("INPUT: "):
            interactive_msg(msg, filltext=70)

        F = readCNF()

    if hasattr(args, "transformation"):
        try:
            G = args.transformation.transform_cnf(F, args)
        except ValueError as e:
            args.transformation.subparser.error(str(e))
    else:
        G = F

    if mode == 'formula':
        return G
    elif mode == 'string':
        return G.dimacs(export_header=args.verbose)
    else:
        with paginate_or_redirect_stdout(args.output):
            print(G.dimacs(export_header=args.verbose))


# Launcher
if __name__ == '__main__':
    setup_SIGINT()

    try:

        command_line_utility(sys.argv)

    except ValueError as e:
        error_msg("DIMACS ERROR: " + str(e))
        sys.exit(-1)

    except CLIError as e:
        error_msg(str(e))
        sys.exit(-1)

    except InternalBug as e:
        print(str(e), file=sys.stderr)
        sys.exit(-1)
