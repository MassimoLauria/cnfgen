#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode dominating set problems
"""

from itertools import combinations

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph
from cnfgen.localtypes import positive_int

def unique_neighborhoods(G):
    """List the neighborhoods of a graph

List sets of vertices, each of them representing a neighborhood in the
graph. Each neighborhood is listed just one. Each one is sorted and
they are enumerated in a sorted fashion."""
    n = G.number_of_vertices()
    if n == 0:
        return []
    neighborhoods = []
    for v in range(1, n+1):
        neighborhoods.append(sorted([v] + list(G.neighbors(v))))
    neighborhoods.sort()
    unique = [neighborhoods[0]]
    for n in neighborhoods:
        if n != unique[-1]:
            unique.append(n)
    return unique



def DominatingSet(G, d, alternative=False, formula_class=CNF):
    r"""Generates the clauses for a dominating set for G of size <= d

    The formula encodes the fact that the graph :math:`G` has
    a dominating set of size :math:`d`. This means that it is possible
    to pick at most :math:`d` vertices in :math:`V(G)` so that all remaining
    vertices have distance at most one from the selected ones.

    Parameters
    ----------
    G : cnfgen.Graph or networkx.Graph
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
    G = Graph.normalize(G, 'G')
    positive_int(d, 'd')

    description = "{}-dominating set on {}".format(d, G.name)
    F = formula_class(description=description)

    # Create variables
    V = G.number_of_vertices()
    D = F.new_block(V, label='x_{{{0}}}')
    M = F.new_mapping(V, d)

    if V == 0:
        return F

    # No two (active) vertices map to the same index
    if alternative:
        for u, v in combinations(range(1,V+1), 2):
            for i in range(1, d + 1):
                F.add_clause([- D(u), -D(v), -M(u, i), - M(v, i)])
    else:
        F.force_injective_mapping(M)

    # (Active) Vertices in the sequence are not repeated
    if alternative:
        for v in range(1,V+1):
            for i, j in combinations(range(1, d + 1), 2):
                F.add_clause([ -D(v), -M(v, i), -M(v,j)])
    else:
        F.force_nondecreasing_mapping(M)

    # D(v) = M(v,1) or M(v,2) or ... or M(v,d)
    if not alternative:
        for i in range(1, d + 1):
            for v in range(1,V+1):
                F.add_clause([-M(v, i), D(v)])
    for v in G.vertices():
        F.add_clause([-D(v)] + list(M(v, None)))

    # Every neighborhood must have a true D variable
    for N in unique_neighborhoods(G):
        F.add_clause([D(v) for v in N])
    return F

def Tiling(G, formula_class=CNF):
    r"""Generates the clauses for a tiling of G

    The formula encodes the fact that the graph :math:`G` has a
    tiling. This means that it is possible to pick a subset of
    vertices :math:`D` so that all vertices have distance at most one
    from exactly one verteix in :math:`D`.

    Parameters
    ----------
    G : cnfgen.Graph or networkx.Graph
        a simple undirected graph

    Returns
    -------
    CNF
       the CNF encoding of a tiling of graph :math:`G`

    """
    # Describe the formula
    G = Graph.normalize(G,'G')
    description = "tiling of {}".format(G.name)

    F = formula_class(description=description)
    x = F.new_block(G.number_of_vertices() , label='x_{{{0}}}')
    # Every neighborhood must have exactly one variable
    for N in unique_neighborhoods(G):
        F.cardinality_eq([x(v) for v in N],1)

    return F
