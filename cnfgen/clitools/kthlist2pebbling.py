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

# Help strings
USAGE_STRING = """usage:
 {0} [-h|--help] [-i <input>] [-o <output>] [<transformation> <args>]
"""

DESCRIPTION_STRING = """Transforms a graph file in kthlist format into a pebbling formula,
with the possibility to apply further transformations to it.

optional arguments:
  -h, --help            show this help message and exit
  --input <input>, -i <input>
                        The DAG is read from a file instead of being
                        read from standard output. Setting '<input>'
                        to '-' is another way to read from standard
                        input. (default: -)
  --output <output>, -o <output>
                        Save the formula to <output>.
                        Setting '<output>' to '-' sends the
                        formula to standard output. (default: -)
  --quiet, -q           Output just the formula with no header.

Choices for <transformation>:
    anybut          substitute x with x1 + x2 + ... + xN != K
    atleast         substitute x with x1 + x2 + ... + xN >= K
    atmost          substitute x with x1 + x2 + ... + xN <= K
    eq              substitute x with predicate x1==x2==...==xN
                    (i.e. all equals)
    exact           substitute x with x1 + x2 + ... + xN == K
    flip            negate all variables in the formula
    ite             substitute x with "if X then Y else Z"
    lift            one dimensional lifting x -> x1 y1 OR ... OR xN yN,
                    with y1 + ... + yN = 1
    maj             substitute x with Majority(x1,x2,...,xN)
    majcomp         variable compression using Majority
    neq             substitute x with |{x1,x2,...,xN}|>1
                    (i.e. not all equals)
    none            no transformation
    one             substitute x with x1 + x2 + ... + xN = 1
    or              substitute variable x with OR(x1,x2,...,xN)
    shuffle         Permute variables, clauses and/or
                    polarity of literals at random
    xor             substitute variable x with XOR(x1,x2,...,xN)
    xorcomp         variable compression using XOR
"""


# Command line helpers
def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.usage = USAGE_STRING.format(parser.prog)
    parser.description = DESCRIPTION_STRING
    parser.add_argument('--output',
                        '-o',
                        type=argparse.FileType('w'),
                        metavar="<output>",
                        default='-')
    parser.add_argument(
        '--input',
        '-i',
        type=argparse.FileType('r'),
        metavar="<input>",
        default='-')
    parser.add_argument('--quiet',
                        '-q',
                        action='store_false',
                        dest='verbose')

    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")

    for sc in get_transformation_helpers():
        p = subparsers.add_parser(sc.name)
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
        return F2.to_dimacs()
    else:
        F2.to_file(args.output, 'dimacs')


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
