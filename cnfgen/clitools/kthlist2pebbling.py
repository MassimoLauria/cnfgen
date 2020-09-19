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

from cnfgen.families.pebbling import PebblingFormula
from cnfgen.graphs import readGraph

from cnfgen.clitools.cmdline import paginate_or_redirect_stdout
from cnfgen.clitools.cmdline import redirect_stdin
from cnfgen.clitools.cmdline import setup_SIGINT
from cnfgen.clitools.cmdline import get_transformation_helpers
from cnfgen.clitools.cmdline import CLIParser, CLIError

from cnfgen.clitools.msg import interactive_msg
from cnfgen.clitools.msg import error_msg
from cnfgen.clitools.msg import msg_prefix
from cnfgen.clitools.msg import InternalBug

#################################################################
#          Command line tool follows
#################################################################


# Command line helpers
def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
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
    parser.add_argument(
        '--input',
        '-i',
        type=argparse.FileType('r'),
        metavar="<input>",
        default='-',
        help=
        """Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
    parser.add_argument('--quiet',
                        '-q',
                        action='store_false',
                        dest='verbose',
                        help="""Output just the formula with no header.""")

    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")

    for sc in get_transformation_helpers():
        p = subparsers.add_parser(sc.name, help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)


# Main program
def cli(argv=sys.argv, mode='output'):
    """From KTHLists to Pebbling formulas

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
    parser = CLIParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)

    # Be lenient on non string arguments
    argv = [str(x) for x in argv]

    args = parser.parse_args(argv[1:])

    ask_kthlist_graph = """
       Waiting for a directed acyclic graph on <stdin>,
       in 'kthlist' format.

       See: https://massimolauria.net/cnfgen/graphformats.html"""

    with redirect_stdin(args.input), msg_prefix('c '):

        with msg_prefix('GRAPH INPUT: '):
            interactive_msg(ask_kthlist_graph)

        G = readGraph(sys.stdin, "dag", file_format="kthlist")

    F = PebblingFormula(G)

    if hasattr(args, "transformation"):
        F2 = args.transformation.transform_cnf(F, args)
    else:
        F2 = F

    if mode == 'formula':
        return F2
    elif mode == 'string':
        return F2.dimacs(export_header=args.verbose)
    else:
        with paginate_or_redirect_stdout(args.output):
            print(F2.dimacs(export_header=args.verbose))


# Launcher
def main():
    setup_SIGINT()
    try:

        cli(sys.argv, mode='output')

    except ValueError as e:
        error_msg("GRAPH ERROR: " + str(e))
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
