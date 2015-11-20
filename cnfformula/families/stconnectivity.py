#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Buss' s-t connectivity formulas
"""

from cnfformula.cnf import CNF

from cnfformula.cmdline import SimpleGraphHelper


import random
import cnfformula.cmdline
import cnfformula.families

from itertools import product

def edgename_g(e):
    return "g_{{{0},{1}}}".format(*sorted(e))
def edgename_r(e):
    return "r_{{{0},{1}}}".format(*sorted(e))

def OneOf(lits):
    yield [(True, l) for l in lits]
    for i in range(len(lits)):
        for j in range(i+1, len(lits)):
            yield [(False, lits[i]), (False, lits[j])]
def ZeroOrTwoOf(lits):
    # not >=3
    for i in range(len(lits)):
        for j in range(i+1, len(lits)):
            for k in range(j+1, len(lits)):
                yield [(False, lits[i]), (False, lits[j]), (False, lits[k])]
    # not ==1
    for i in range(len(lits)):
        yield [(False, lits[i])] + [(True, lits[j]) for j in range(len(lits)) if j!=i]

@cnfformula.families.register_cnf_generator
def STConnFormula(graph, s_g, t_g, s_r, t_r):
    """Build an s-t connectivity formula based on the input graph
    and source/sink vertices for the green and red path.
    A description can be found in [1]_.

    Arguments:
    - `graph`: input graph
    - `s_g`: source vertex of the green path.
    - `t_g`: sink vertex of the green path.
    - `s_r`: source vertex of the red path.
    - `t_r`: sink vertex of the red path.

    References
    ----------
    .. [1] S.R. Buss
           Polynomial-Size Frege and Resolution Proofs of
           st-Connectivity and Hex Tautologies
           Theoretical Computer Science 357, 1-3 (2006) 35-52.

    """
    V=sorted(graph.nodes())

    # init formula
    formula = CNF()
    for e in sorted(graph.edges(),key=sorted):
        formula.add_variable(edgename_g(e))
        formula.add_variable(edgename_r(e))

    for v in V:
        # green
        f_g = OneOf if v in (s_g, t_g) else ZeroOrTwoOf
        for cls in f_g([ edgename_g(e) for e in graph.edges_iter(v) ]):
            formula.add_clause(list(cls),strict=True)
        # red
        f_r = OneOf if v in (s_r, t_r) else ZeroOrTwoOf
        for cls in f_r([ edgename_r(e) for e in graph.edges_iter(v) ]):
            formula.add_clause(list(cls),strict=True)
        # at most in one
        for e1,e2 in product(graph.edges_iter(v),graph.edges_iter(v)):
            formula.add_clause([(False, edgename_g(e1)), (False, edgename_r(e2))])

    return formula
