#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF Formulas for Ramsey-like statements

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""


from cnfformula import CNF
from cnfformula.cmdline import is_formula_cmdhelper    

from textwrap import dedent
from itertools import combinations


def RamseyLowerBoundFormula(s,k,N):
    """Formula claiming that Ramsey number r(s,k) > N

    Arguments:
    - `s`: independent set size
    - `k`: clique size
    - `N`: vertices
    """

    ram=CNF()

    ram.header=dedent("""\
        CNF encoding of the claim that there is a graph of %d vertices
        with no independent set of size %d and no clique of size %d
        """ % (N,s,k)) + ram.header

    #
    # No independent set of size s
    #
    for vertex_set in combinations(xrange(1,N+1),s):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause += [(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    #
    # No clique of size k
    #
    for vertex_set in combinations(xrange(1,N+1),k):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause+=[(False,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    return ram



### Formula families
    
    
class RamseyCmdHelper(object):
    """Command line helper for RamseyNumber formulas
    """
    name='ram'
    description='ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',metavar='<s>',type=int,help="Forbidden independent set size")
        parser.add_argument('k',metavar='<k>',type=int,help="Forbidden independent clique")
        parser.add_argument('N',metavar='<N>',type=int,help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyLowerBoundFormula(args.s, args.k, args.N)


