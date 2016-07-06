#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to build dimacs encoding of pebbling formulas

Accepts only the kthlist graph format:

ASSUMPTIONS: the graph is given with a line for each vertex, from
sources to a *single sink*.

CNF formulas interesting for proof complexity.
"""

from __future__ import print_function

import os

import cnfformula
import cnfformula.graphs as graphs
import sys
import argparse

#################################################################
#          Command line tool follows
#################################################################


###
### Command line helpers
###

def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
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
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)


    
    # Cmdline parser for formula transformations    
    from cnfformula import transformations
    from cnfformula.cmdline import is_cnf_transformation_subcommand
    from cnfformula.cmdline import find_methods_in_package

    subparsers = parser.add_subparsers(title="Available transformation",
                                       metavar="<transformation>")
    for sc in find_methods_in_package(transformations,
                                      is_cnf_transformation_subcommand,
                                      sortkey=lambda x:x.name):
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)



###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    assert insignal!=None
    assert frame!=None
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)
    args=parser.parse_args(argv[1:])

    G = graphs.readGraph(args.input,"dag",file_format="kthlist")

    Fstart = cnfformula.PebblingFormula(G)

    Ftransform = args.transformation.transform_cnf(Fstart,args)
    print(Ftransform.dimacs(),file=args.output)
    
### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
