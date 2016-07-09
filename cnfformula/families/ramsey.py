#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF Formulas for Ramsey-like statements
"""

from cnfformula.cnf import CNF

import cnfformula.cmdline
import cnfformula.families

from textwrap import dedent
from itertools import combinations
from math import sqrt

@cnfformula.families.register_cnf_generator
def PythagoreanTriples(N):
    """There is a Pythagorean triples free coloring on N 
    
    The formula claims that it is possible to bicolor the numbers from
    1 to :math:`N` so that there  is no monochromatic triplet 
    :math:`(x,y,z)` so that :math:`x^2+y^2=z^2`.

    Parameters
    ----------
    N  : int
         size of the interval

    Return
    ------
    A CNF object

    Raises
    ------
    ValueError
       Parameters are not positive integers

    References
    ----------
    .. [1] M. J. Heule, O. Kullmann, and V. W. Marek. 
           Solving and verifying the boolean pythagorean triples problem via cube-and-conquer. 
           arXiv preprint arXiv:1605.00723, 2016.
    """

    ptn=CNF()

    ptn.header=dedent("""
It is possible to bicolor the numbers from
1 to {} so that there  is no monochromatic triplets
(x,y,z) such that x^2+y^2=z^2

""".format(N)) + ptn.header

    def V(i):
        return "x_{{{}}}".format(i)

    # Variables represent the coloring of the number
    for i in xrange(1,N+1):
        ptn.add_variable(V(i))

        
    for x,y in combinations(range(1,N+1),2):
        z = int(sqrt(x**2 +  y**2))
        if z <=N and z**2 == x**2 + y**2:
            ptn.add_clause([ (True, V(x)), (True, V(y)), (True, V(z))],strict=True)
            ptn.add_clause([ (False,V(x)), (False,V(y)), (False,V(z))],strict=True)

    return ptn



@cnfformula.families.register_cnf_generator
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
    # One variable per edge (indices are ordered)
    #
    for edge in combinations(xrange(1,N+1),2):
        ram.add_variable('e_{{{0},{1}}}'.format(*edge))
    
    #
    # No independent set of size s
    #
    for vertex_set in combinations(xrange(1,N+1),s):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause += [(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause,strict=True)

    #
    # No clique of size k
    #
    for vertex_set in combinations(xrange(1,N+1),k):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause+=[(False,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause,strict=True)

    return ram



### Formula families
    
@cnfformula.cmdline.register_cnfgen_subcommand
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


@cnfformula.cmdline.register_cnfgen_subcommand
class PTNCmdHelper(object):
    """Command line helper for PTN formulas
    """
    name='ptn'
    description='Bicoloring of N with no monochromatic Pythagorean Triples'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for PTN formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="Size of the domain")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PythagoreanTriples(args.N)


