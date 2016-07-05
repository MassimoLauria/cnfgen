#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to build dimacs encoding of pebbling formulas

Accepts only the adjacency list graph format:

ASSUMPTIONS: the graph is given with a line for each vertex, from
sources to a *single sink*.

CNF formulas interesting for proof complexity.
"""

from __future__ import print_function

import os

import cnfformula
import sys
import argparse
from itertools import product

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

def pebbling_formula_compressed_clauses(adjfile):
    """
    Read a graph from file, in the adjacency lists format. And output the list of
    compressed clauses representing the pebbling formula.

    The vertices MUST be listed from to sources to the *A SINGLE
    SINK*.  In a topologically sorted fashion.
    
    Arguments:
    - `inputfile`:  file handle of the input

    """

    for l in adjfile.readlines():
        
        # ignore comments
        if l[0]=='c':
            continue

        if ':' not in l:
            continue # vertex number spec

        target,sources=l.split(':')
        target=int(target.strip())
        yield [ -int(i) for i in sources.split() ]+[target]

    yield [-target]


def transform_compressed_clauses(clauses,pattern):
    """Apply to clauses the transformation applied to a pattern formula

    Build new clauses by appling exactly the same transformation
    applied to a pattern CNF. It works on the compressed
    representation the clauses: both input and output of this
    transformation is a list of tuples of literals represented
    as integer.

    E.g. [(-1,2,3), (-2,1,5), (3,4,5)]

    Very HACKING implementation

    Parameters
    ----------
    clauses: list(tuple(int))
        a sequence of clause in compressed format

    pattern : a CNF 
        this CNF must have been subjected to the same transformation, and 
        the transformed formula must have at least a variable
    """

    # We need one variable from the pattern
    assert len(list(pattern._orig_cnf.variables()))>0
    pattern_var = list(pattern._orig_cnf.variables())[0]
    
    varlift    =pattern.transform_variable_preamble(pattern_var)
    poslift    =pattern.transform_a_literal(True, pattern_var)
    neglift    =pattern.transform_a_literal(False,pattern_var)

    varlift    = [list(pattern._compress_clause(cls)) for cls in varlift ]
    poslift    = [list(pattern._compress_clause(cls)) for cls in poslift ]
    neglift    = [list(pattern._compress_clause(cls)) for cls in neglift ]
    offset     = len(list(pattern.variables()))

    # information about the input formula
    input_variables = 0

    output_clauses   = 0
    output_variables = 0

    def substitute(literal):
        if literal>0:
            var=literal
            lift=poslift
        else:
            var=-literal
            lift=neglift

        substitute.max=max(var,substitute.max)
        return [[ (l/abs(l))*offset*(var-1)+l for l in cls ] for cls in lift]

    substitute.max=0
           
    for cls in clauses:

        # a substituted clause is the OR of the substituted literals
        domains=[ substitute(lit) for lit in cls ]
        domains=tuple(domains)

        for clause_tuple in product(*domains):
            output_clauses +=1
            yield [lit for clause in clause_tuple for lit in clause ]

    # count the variables
    input_variables  = substitute.max
    output_variables = input_variables*offset

    for i in xrange(input_variables):
        for cls in varlift:
            output_clauses += 1
            yield [ (l/abs(l))*offset*i+l for l in cls ]


### Produce the dimacs output from the data
def kthlist2pebbling(inputfile, output, args):
    # Build the lifting mechanism

    # Generate the basic formula
    from cStringIO import StringIO
    output_cache=StringIO()

    pattern = args.transformation.transform_cnf(
        cnfformula.CNF([[(True,'y')]]),
        args)
    
    cls_iter=transform_compressed_clauses(
        pebbling_formula_compressed_clauses(inputfile),
        pattern)

    for cls in cls_iter:
        print(" ".join([str(l) for l in cls])+" 0",file=output_cache)
            
    # except StopClauses as cnfinfo:

    #     print("p cnf {} {}".format(cnfinfo.variables,cnfinfo.clauses),
    #           file=output)
    output.write(output_cache.getvalue())
    #return cnfinfo

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

    kthlist2pebbling(args.input, args.output, args)
    
### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
