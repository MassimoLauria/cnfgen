#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `dimacs` contains facilities to generate manipulates dimacs
CNFs, in particular from command line.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import sys
import random
from cnfformula import CNF
from cnfformula.utils import dimacs2cnf


def reshuffle(cnf,
              variable_permutation=None,
              clause_permutation=None,
              polarity_flip=None
              ):
    """ Reshuffle the given cnf. Returns a formula logically
    equivalent to the input with the following transformations
    applied in order:

    1. Polarity flips. polarity_flip is a {-1,1}^n vector. If the i-th
    entry is -1, all the literals with the i-th variable change its
    sign.

    2. Variable permutations. variable_permutation is a permutation of
    [vars(cnf)]. All the literals with the old i-th variable are
    replaced with the new i-th variable.

    3. Clause permutations. clause_permutation is a permutation of
    [0..m-1]. The resulting clauses are reordered according to the
    permutation.
"""

    # empty cnf
    out=CNF(header='')

    out.header="Reshuffling of:\n\n"+cnf.header


    vars=list(cnf.variables())
    N=len(vars)
    M=len(cnf)

    # variable permutation
    if variable_permutation==None:
        variable_permutation=vars
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation)==N

    # polarity flip
    if polarity_flip==None:
        polarity_flip=[1-2*random.randint(0,1)
                              for i in xrange(N)]
    else:
        assert len(polarity_flip)==N

    #
    # substitution of variables
    #
    for v in variable_permutation:
        out.add_variable(v)

    substitution=[None]*(2*N+1)
    reverse_idx=dict([(v,i) for (i,v) in enumerate(out.variables(),1)])
    polarity_flip = [None]+polarity_flip

    for i,v in enumerate(cnf.variables(),1):
        substitution[i]=  polarity_flip[i]*reverse_idx[v]
        substitution[-i]= -substitution[i]

    #
    # permutation of clauses
    #
    if clause_permutation==None:
        clause_permutation=range(M)
        random.shuffle(clause_permutation)

    # load clauses
    out._clauses = [None]*M
    for (old,new) in enumerate(clause_permutation):
        out._clauses[new]=tuple( substitution[l] for l in cnf._clauses[old])

    # load comments
    assert len(out._comments)==0
    clause_permutation.append((M,M)) # comments after last clause do not move
    for (pos,text) in cnf._comments:
        out._comments.append((clause_permutation[pos],text))
    clause_permutation.pop()
    def key(t): return t[0]
    out._comments.sort(key=key)


    # return the formula
    assert out._check_coherence(force=True)
    return out


def command_line_reshuffle(argv):

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
    parser=argparse.ArgumentParser(prog='shuffle',epilog="""
    For more information type 'shuffle <formula type> [--help | -h ]'
    """)

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
    parser.add_argument('--seed','-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)

    g=parser.add_mutually_exclusive_group()
    g.add_argument('--verbose', '-v',action='count',default=1,
                   help="""Include comments inside the formula. It may
                   not be supported by very old sat solvers.
                   """)
    g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                   help="""Output just the formula with not header
                   or comment.""")


    # Process the options
    args=parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    input_cnf=dimacs2cnf(args.input)

    output_cnf=reshuffle(input_cnf)

    # Do we wnat comments or not
    output_comments=args.verbose >= 2
    output_header  =args.verbose >= 1

    output_cnf.dimacs_dump(add_header=output_header,
                           add_comments=output_comments,
                           output=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_reshuffle(sys.argv)
