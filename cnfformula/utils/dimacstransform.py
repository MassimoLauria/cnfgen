#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF transformation, it increases the hardness of a CNF.

This is the implementation of a command line utility that transform
CNF files in DIMACS format into new  CNFs

Utilities to apply to a dimacs CNF file, a transformation which
increase the hardness of the formula

Accept a cnf in dimacs format in input
"""

from __future__ import print_function
import os

from . import dimacs2cnf


import sys
import argparse
import cnfformula

def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The input formula is read as a dimacs CNF file file
                        instead of standard input. Setting '<input>'
                        to '-' is another way to read from standard
                        input. (default: -) """)

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
    assert(insignal!=None)
    assert(frame!=None)
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)
    args=parser.parse_args(argv[1:])
    F = dimacs2cnf(args.input)
    G = args.transformation.transform_cnf(F,args)
    print(G.dimacs(),file=args.output)

    
### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
