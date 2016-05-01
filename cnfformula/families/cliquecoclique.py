#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from cnfformula.cnf import CNF
from cnfformula.cnf import greater_or_equal_constraint
from cnfformula.cnf import less_or_equal_constraint

import cnfformula.cmdline
import cnfformula.families

from itertools import combinations, permutations

@cnfformula.families.register_cnf_generator
def CliqueCoclique(n,m):
    """Clique-coclique CNF formula [1]_

    The formula claims that a graph with an m-clique is not
    (m-1)-colourable.

    Arguments:
    - `n`: number of vertices in the graph
    - `m`: size of the clique

    References
    ----------
    .. [1] Pavel Pudlak
           Lower bounds for resolution and cutting plane proofs and
           monotone computations.
           Journal of Symbolic Logic (1997)

    """

    def P(i,j):
        return 'p_{{{0},{1}}}'.format(i,j)
    def Q(k,i):
        return 'q_{{{0},{1}}}'.format(k,i)
    def R(i,l):
        return 'r_{{{0},{1}}}'.format(i,l)
    
    formula=CNF()
    formula.header="Clique-coclique formula for {0} vertices and clique size {1}\n".format(n,m)\
        + formula.header

    for i in range(1,n+1):
        for j in range(i+1,n+1):
            formula.add_variable(P(i,j))
    for k in range(1,m+1):
        for i in range(1,n+1):
            formula.add_variable(Q(k,i))
    for i in range(1,n+1):
        for ell in range(1,m):
            formula.add_variable(R(i,ell))
    for k in range(1,m+1):
        formula.add_clause([(True, Q(k,i)) for i in range(1,n+1)], strict=True)
    for i in range(1,n+1):
        for k,k_ in combinations(range(1,m+1),2):
            formula.add_clause([(False, Q(k,i)), (False, Q(k_,i))], strict=True)
    for i,j in combinations(range(1,n+1),2):
        for k,k_ in permutations(range(1,m+1),2):
            formula.add_clause([(True, P(i,j)), (False, Q(k,i)), (False, Q(k_,j))], strict=True)
    for i in range(1,n+1):
        formula.add_clause([(True, R(i,ell)) for ell in range(1,m)], strict=True)
    for i,j in combinations(range(1,n+1),2):
        for ell in range(1,m):
            formula.add_clause([(False, P(i,j)), (False, R(i,ell)), (False, R(j,ell))], strict=True)
    #print(formula.clauses())
    return formula

@cnfformula.cmdline.register_cnfgen_subcommand
class CliqueCocliqueCmdHelper(object):
    """Command line helper for the Clique-coclique CNF"""
    
    name='cliquecoclique'
    description='clique-coclique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for clique-coclique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('n',metavar='<n>',type=int,help="Number of vertices")
        parser.add_argument('m',metavar='<m>',type=int,help="Clique size")

    @staticmethod
    def build_cnf(args):
        """Build a Clique-coclique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CliqueCoclique(args.n,args.m)

