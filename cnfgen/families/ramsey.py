#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF Formulas for Ramsey-like statements
"""

from cnfgen.cnf import CNF

from textwrap import dedent
from itertools import combinations
from math import sqrt


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

    description = "Pythagorean triples problem on 1...{}".format(N)
    ptn = CNF(description=description)

    def V(i):
        return "x_{{{}}}".format(i)

    # Variables represent the coloring of the number
    for i in range(1, N + 1):
        ptn.add_variable(V(i))

    for x, y in combinations(range(1, N + 1), 2):
        z = int(sqrt(x**2 + y**2))
        if z <= N and z**2 == x**2 + y**2:
            ptn.add_clause([(True, V(x)), (True, V(y)), (True, V(z))],
                           strict=True)
            ptn.add_clause([(False, V(x)), (False, V(y)), (False, V(z))],
                           strict=True)

    return ptn


def RamseyLowerBoundFormula(s, k, N):
    """Formula claiming that Ramsey number r(s,k) > N

    Arguments:
    - `s`: independent set size
    - `k`: clique size
    - `N`: vertices
    """

    description = "{}-vertices graph free of {}-independent sets and {}-cliques".format(
        N, s, k)
    ram = CNF(description=description)

    def V(i):
        return "x_{{{}}}".format(i)

    #
    # One variable per edge (indices are ordered)
    #
    for edge in combinations(range(1, N + 1), 2):
        ram.add_variable('e_{{{0},{1}}}'.format(*edge))

    #
    # No independent set of size s
    #
    for vertex_set in combinations(range(1, N + 1), s):
        clause = []
        for edge in combinations(vertex_set, 2):
            clause += [(True, 'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause, strict=True)

    #
    # No clique of size k
    #
    for vertex_set in combinations(range(1, N + 1), k):
        clause = []
        for edge in combinations(vertex_set, 2):
            clause += [(False, 'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause, strict=True)

    return ram
