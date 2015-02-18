#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os

from .. import available_transform
from ..transformation import transform_compressed_clauses,StopClauses


__docstring__ =\
"""Utilities to build dimacs encoding of pebbling formulas

Accept a KTH specific graph format:

ASSUMPTIONS: the graph is given with a line for each vertex, from
sources to a *single sink*.

CNF formulas interesting for proof complexity.

Copyright (C) 2012, 2013, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import sys
import argparse

#################################################################
#          Command line tool follows
#################################################################


class HelpTransformAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpTransformAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Formula transformations available
        """)
        for k,entry in available_transform().iteritems():
            print("{}\t:  {}".format(k,entry[0]))
        print("\n")
        sys.exit(0)

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

    g=parser.add_mutually_exclusive_group()
    g.add_argument('--noheader', '-n',action='store_false',dest='header',
                   help="""Do not output the preamble, so that formula generation is faster (one
                           pass on the data).""")
    parser.add_argument('--Transform','-T',
                        metavar="<transformation method>",
                        choices=available_transform().keys(),
                        default='none',
                        help="""
                        Transform the CNF formula to make it harder.
                        See `--help-transformation` for more informations
                        """)
    parser.add_argument('--Tarity','-Ta',
                        metavar="<transformation arity>",
                        type=int,
                        default=None,
                        help="""
                        Hardness parameter for the transformation procedure.
                        See `--help-transform` for more informations
                        """)
    parser.add_argument('--help-transform',nargs=0,action=HelpTransformAction,help="""
                        Formula can be made harder applying some
                        so called "transformation procedures".
                        This gives information about the implemented transformation.
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


def pebbling_formula_compressed_clauses(kthfile):
    """
    Read a graph from file, in the KTH format. And output the list of
    compressed clauses representing the pebbling formula.

    The vertices MUST be listed from to sources to the *A SINGLE
    SINK*.  In a topologically sorted fashion.
    
    Arguments:
    - `inputfile`:  file handle of the input

    """

    for l in kthfile.readlines():
        
        # ignore comments
        if l[0]=='c':
            continue

        if ':' not in l:
            continue # vertex number spec

        target,sources=l.split(':')
        target=int(target.strip())
        yield [ -int(i) for i in sources.split() ]+[target]

    yield [-target]


### Produce the dimacs output from the data
def kthgraph2dimacs(inputfile, method, rank, output, header=True):
    # Build the lifting mechanism

    # Generate the basic formula
    if header:
        
        from cStringIO import StringIO
        output_cache=StringIO()

    else:
        output_cache=output
        
    cls_iter=transform_compressed_clauses(
                    pebbling_formula_compressed_clauses(inputfile),
                    method,rank)

    try:

        while True:
            cls = cls_iter.next()
            print(" ".join([str(l) for l in cls])+" 0",file=output_cache)
            
    except StopClauses as cnfinfo:

        if header:
            # clauses cached in memory
            print("p cnf {} {}".format(cnfinfo.variables,cnfinfo.clauses),
                  file=output)
            output.write(output_cache.getvalue())

        else:
            # clauses have been already sent to output
            pass    
        return cnfinfo

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
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]))
    setup_command_line(parser)

    # Process the options
    args=parser.parse_args(argv[1:])

    kthgraph2dimacs(args.input, args.Transform, args.Tarity, args.output, args.header)

### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
