#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode dominating set problems
"""

from cnfgen.cnf import CNF

from cnfgen.graphs import enumerate_vertices, enumerate_edges, neighbors
from itertools import combinations, combinations_with_replacement, product


def DominatingSet(G, d, alternative=False):
    r"""Generates the clauses for a dominating set for G of size <= d

    The formula encodes the fact that the graph :math:`G` has
    a dominating set of size :math:`d`. This means that it is possible
    to pick at most :math:`d` vertices in :math:`V(G)` so that all remaining
    vertices have distance at most one from the selected ones.

    Parameters
    ----------
    G : networkx.Graph
        a simple undirected graph
    d : a positive int
        the size limit for the dominating set
    alternative : bool
        use an alternative construction that 
        is provably hard from resolution proofs.

    Returns
    -------
    CNF
       the CNF encoding for dominating of size :math:`\leq d` for graph :math:`G`

    """
    # Describe the formula
    description = "{}-dominating set".format(d)

    if hasattr(G, 'name'):
        description += " on " + G.name

    F = CNF(description=description)

    if not isinstance(d, int) or d < 1:
        ValueError("Parameter \"d\" is expected to be a positive integer")

    # Fix the vertex order
    V = enumerate_vertices(G)

    def D(v):
        return "x_{{{0}}}".format(v)

    def M(v, i):
        return "g_{{{0},{1}}}".format(v, i)

    def N(v):
        return tuple(sorted([v] + [u for u in G.neighbors(v)]))

    # Create variables
    for v in V:
        F.add_variable(D(v))
    for i, v in product(range(1, d + 1), V):
        F.add_variable(M(v, i))

    # No two (active) vertices map to the same index
    if alternative:
        for u, v in combinations(V, 2):
            for i in range(1, d + 1):
                F.add_clause([(False, D(u)), (False, D(v)), (False, M(u, i)),
                              (False, M(v, i))])
    else:
        for i in range(1, d + 1):
            for c in CNF.less_or_equal_constraint([M(v, i) for v in V], 1):
                F.add_clause(c)

    # (Active) Vertices in the sequence are not repeated
    if alternative:
        for v in V:
            for i, j in combinations(range(1, d + 1), 2):
                F.add_clause([(False, D(v)), (False, M(v, i)), (False, M(v,
                                                                         j))])
    else:
        for i, j in combinations_with_replacement(range(1, d + 1), 2):
            i, j = min(i, j), max(i, j)
            for u, v in combinations(V, 2):
                u, v = max(u, v), min(u, v)
                F.add_clause([(False, M(u, i)), (False, M(v, j))])

    # D(v) = M(v,1) or M(v,2) or ... or M(v,d)
    if not alternative:
        for i, v in product(range(1, d + 1), V):
            F.add_clause([(False, M(v, i)), (True, D(v))])
    for v in V:
        F.add_clause([(False, D(v))] + [(True, M(v, i))
                                        for i in range(1, d + 1)])

    # Every neighborhood must have a true D variable
    neighborhoods = sorted(set(N(v) for v in V))
    for N in neighborhoods:
        F.add_clause([(True, D(v)) for v in N])

    return F

def Tiling(G):
    r"""Generates the clauses for a tiling of G

    The formula encodes the fact that the graph :math:`G` has a
    tiling. This means that it is possible to pick a subset of
    vertices :math:`D` so that all vertices have distance at most one
    from exactly one verteix in :math:`D`.

    Parameters
    ----------
    G : networkx.Graph
        a simple undirected graph

    Returns
    -------
    CNF
       the CNF encoding of a tiling of graph :math:`G`

    """
    # Describe the formula
    description = "tiling"

    if hasattr(G, 'name'):
        description += " of " + G.name

    F = CNF(description=description)

    # Fix the vertex order
    V=enumerate_vertices(G)

    def D(v):
        return "x_{{{0}}}".format(v)

    def N(v):
        return tuple(sorted([v] + [u for u in G.neighbors(v)]))

    # Create variables
    for v in V:
        F.add_variable(D(v))

    # Every neighborhood must have exactly one true D variable
    neighborhoods = sorted(set(N(v) for v in V))
    for N in neighborhoods:
        for cls in CNF.equal_to_constraint([D(v) for v in N], 1):
            F.add_clause(list(cls), strict=True)

    return F
