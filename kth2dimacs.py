#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

from cnfformula import CNF
from cnfformula import available_lifting,LiftFormula
from itertools  import product
import random

__docstring__ =\
"""Utilities to build dimacs encoding of pebbling formulas

Accept a KTH specific graph format:

ASSUMPTIONS: the graph is given with a line for each vertex, from
sources to a *single sink*.

CNF formulas interesting for proof complexity.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import sys
import argparse

#################################################################
#          Command line tool follows
#################################################################


class HelpLiftingAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpLiftingAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Liftings/Substitutions available
        """)
        for k,entry in available_lifting().iteritems():
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
    parser.add_argument('--lift','-l',
                        metavar="<lifting method>",
                        choices=available_lifting().keys(),
                        default='none',
                        help="""
                        Apply a lifting procedure to make the CNF harder.
                        See `--help-lifting` for more informations
                        """)
    parser.add_argument('--liftrank','-lr',
                        metavar="<lifting rank>",
                        type=int,
                        default=None,
                        help="""
                        Hardness parameter for the lifting procedure.
                        See `--help-lifting` for more informations
                        """)
    parser.add_argument('--noise',
                        type=int,
                        default=None,
                        help="""
                        Add noise clauses that propagate truthness from top to bottom
                        """)
    parser.add_argument('--help-lifting',nargs=0,action=HelpLiftingAction,help="""
                         Formula can be made harder applying some
                         so called "lifting procedures".
                         This gives information about the implemented lifting.
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


def pebbling_formula_clauses(kthfile):
    """Read a graph from file, in the KTH format.

    The vertices MUST be listed from to sources to the *A SINGLE
    SINK*.  In a topologically sorted fashion.
    
    Arguments:
    - `inputfile`:  file handle of the input
    """

    for l in kthfile.readlines():
        
        # add the comment to the header
        if l[0]=='c':
            continue

        if ':' not in l:
            continue # vertex number spec

        target,sources=l.split(':')
        target=int(target.strip())
        yield [ -int(i) for i in sources.split() ]+[target]

    yield [-target]


### Lift clauses

class StopClauses(StopIteration):
    """Exception raised when an iterator of clauses finish.

    Attributes:
        variables -- number of variables in the clause stream
        clauses   -- number of clauses streamed
    """

    def __init__(self, variables, clauses):
        self.variables = variables
        self.clauses = clauses

    
def lift(clauses,lift_method='none',lift_rank=None, noise=None):
    """Build a new CNF with by lifing the old CNF

    Arguments:
    - `clauses`: a sequence of clause in DIMACS format
    
    A positive value of `noise` adds random "noise clauses" to the end
    of the formula. The noise clauses will have width `noise`.

    The idea behind these noise clauses is that, although we cannot
    formally prove it, the intuition is that these clauses should not
    change the space complexity in any meaningful way. However, if
    these clauses are smaller than most of the original relevant
    clauses of the formula, then maybe, just maybe, we can hope to
    fool the preprocessor into focusing mostly on these noise clauses
    and ignore the original clauses that it should work on in order to
    make progress. But whether this actually happens is an entirely
    open question and remains to be determined by experiments.
    """

    # Use a dummy lifting operation to get information about the
    # lifting structure.
    poslift=None
    neglift=None
    
    dummycnf=CNF([[(True, "x")]])
    dummycnf=LiftFormula(dummycnf,lift_method,lift_rank)

    varlift    =dummycnf.lift_variable_preamble("x")
    poslift    =dummycnf.lift_a_literal(True,"x")
    neglift    =dummycnf.lift_a_literal(False,"x")

    varlift    = [list(dummycnf._compress_clause(cls)) for cls in varlift ]
    poslift    = [list(dummycnf._compress_clause(cls)) for cls in poslift ]
    neglift    = [list(dummycnf._compress_clause(cls)) for cls in neglift ]
    offset     = len(list(dummycnf.variables()))

    # information about the input formula
    input_clauses   = 0
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

        input_clauses +=1

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

    # partition the input variables into groups of size `noise`
    # randomly, sort them in decreasing order and then add clauses of
    # the form
    # 
    # ¬ x_{i_1}^j v ¬ x_{i_2}^j v ... v ¬ x_{i_(noise-1)}^j v x_{i_noise}^j
    # 
    # for j in [1..rank]
    if (noise) :
        vertices=range(input_variables)
        random.shuffle(vertices)
        for edge in zip(*[iter(vertices)]*noise) :
            for l in xrange(offset) :
                output_clauses += 1
                yield [(1 if i else -1)*(offset*var+l+1) for i,var in enumerate(sorted(edge))]

    raise StopClauses(output_variables,output_clauses)
    

def kth2dimacs(input, liftname, liftrank, output, header=True, comments=True, noise=None) :
    # Build the lifting mechanism

    # Generate the basic formula
    if header:
        
        from cStringIO import StringIO
        output_cache=StringIO()

    else:
        output_cache=output
        
    cls_iter=lift(pebbling_formula_clauses(input),liftname,liftrank, noise)

    try:

        while True:
            cls = cls_iter.next()
            print(" ".join([str(l) for l in cls])+" 0",file=output_cache)
            
    except StopClauses as cnfinfo:

        if comments:
            print("c Pebbling CNF with lifting \'{}\' of rank {}".format(liftname,liftrank),
                  file=output)

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
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv):

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
    parser=argparse.ArgumentParser(prog='kth2dimacs',epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    setup_command_line(parser)

    # Process the options
    args=parser.parse_args(argv)

    kth2dimacs(args.input, args.lift, args.liftrank, args.output, header = args.header, noise = args.noise)

### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv[1:])
