#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the clique-coloring formula 
"""

from cnfgen.cnf import CNF
from itertools import combinations, permutations


def CliqueColoring(n, k, c):
    r"""Clique-coloring CNF formula 

    The formula claims that a graph :math:`G` with :math:`n` vertices
    simultaneously contains a clique of size :math:`k` and a coloring
    of size :math:`c`.

    If :math:`k = c + 1` then the formula is clearly unsatisfiable,
    and it is the only known example of a formula hard for cutting
    planes proof system. [1]_

    Variables :math:`e_{u,v}` to encode the edges of the graph.
    
    Variables :math:`q_{i,v}` encode a function from :math:`[k]` to
    :math:`[n]` that represents a clique.
    
    Variables :math:`r_{v,\ell}` encode a function from :math:`[n]` to
    :math:`[c]` that represents a coloring.
     
    Parameters
    ----------
    n : number of vertices in the graph
    k : size of the clique
    c : size of the coloring

    Returns
    -------
    A CNF object

    References
    ----------
    .. [1] Pavel Pudlak.
           Lower bounds for resolution and cutting plane proofs and
           monotone computations.
           Journal of Symbolic Logic (1997)

    """
    def E(u, v):
        "Name of an edge variable"
        return 'e_{{{0},{1}}}'.format(min(u, v), max(u, v))

    def Q(i, v):
        "Name of an edge variable"
        return 'q_{{{0},{1}}}'.format(i, v)

    def R(v, ell):
        "Name of an coloring variable"
        return 'r_{{{0},{1}}}'.format(v, ell)

    description = "There is a graph of {0} vertices with a {1}-clique and a {2}-coloring".format(
        n, k, c)
    formula = CNF(description=description)
    # Edge variables
    for u in range(1, n + 1):
        for v in range(u + 1, n + 1):
            formula.add_variable(E(u, v))
    # Clique encoding variables
    for i in range(1, k + 1):
        for v in range(1, n + 1):
            formula.add_variable(Q(i, v))
    # Coloring encoding variables
    for v in range(1, n + 1):
        for ell in range(1, c + 1):
            formula.add_variable(R(v, ell))

    # some vertex is i'th member of clique
    for k in range(1, k + 1):
        for cl in CNF.equal_to_constraint([Q(k, v) for v in range(1, n + 1)],
                                          1):
            formula.add_clause(cl, strict=True)

    # clique members are connected by edges
    for v in range(1, n + 1):
        for i, j in combinations(range(1, k + 1), 2):
            formula.add_clause([(False, Q(i, v)), (False, Q(j, v))],
                               strict=True)
    for u, v in combinations(range(1, n + 1), 2):
        for i, j in permutations(range(1, k + 1), 2):
            formula.add_clause([(True, E(u, v)), (False, Q(i, u)),
                                (False, Q(j, v))],
                               strict=True)

    # every vertex v has exactly one colour
    for v in range(1, n + 1):
        for cl in CNF.equal_to_constraint(
            [R(v, ell) for ell in range(1, c + 1)], 1):
            formula.add_clause(cl, strict=True)

    # neighbours have distinct colours
    for u, v in combinations(range(1, n + 1), 2):
        for ell in range(1, c + 1):
            formula.add_clause([(False, E(u, v)), (False, R(u, ell)),
                                (False, R(v, ell))],
                               strict=True)
    return formula
