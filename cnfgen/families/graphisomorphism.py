#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Graph isomorphimsm/automorphism formulas
"""

from cnfgen.cnf import CNF

from cnfgen.graphs import enumerate_vertices
from itertools import combinations, product


def _graph_isomorphism_var(u, v):
    """Standard variable name"""
    return "x_{{{0},{1}}}".format(u, v)


def GraphIsomorphism(G1, G2):
    """Graph Isomorphism formula

    The formula is the CNF encoding of the statement that two simple
    graphs G1 and G2 are isomorphic.

    Parameters
    ----------
    G1 : networkx.Graph
        an undirected graph object
    G2 : networkx.Graph
        an undirected graph object

    Returns
    -------
    A CNF formula which is satiafiable if and only if graphs G1 and G2
    are isomorphic.

    """
    description = "Graph isomorphism between (1) '{}' and (2) '{}'"
    description = description.format(G1.name, G2.name)

    F = CNF(description=description)

    U = enumerate_vertices(G1)
    V = enumerate_vertices(G2)
    var = _graph_isomorphism_var

    for (u, v) in product(U, V):
        F.add_variable(var(u, v))

    # Defined on both side
    for u in U:
        F.add_clause([(True, var(u, v)) for v in V], strict=True)

    for v in V:
        F.add_clause([(True, var(u, v)) for u in U], strict=True)

    # Injective on both sides
    for u in U:
        for v1, v2 in combinations(V, 2):
            F.add_clause([(False, var(u, v1)), (False, var(u, v2))],
                         strict=True)
    for v in V:
        for u1, u2 in combinations(U, 2):
            F.add_clause([(False, var(u1, v)), (False, var(u2, v))],
                         strict=True)

    # Edge consistency
    for u1, u2 in combinations(U, 2):
        for v1, v2 in combinations(V, 2):
            if G1.has_edge(u1, u2) != G2.has_edge(v1, v2):
                F.add_clause([(False, var(u1, v1)), (False, var(u2, v2))],
                             strict=True)
                F.add_clause([(False, var(u1, v2)), (False, var(u2, v1))],
                             strict=True)

    return F


def GraphAutomorphism(G):
    """Graph Automorphism formula

    The formula is the CNF encoding of the statement that a graph G
    has a nontrivial automorphism, i.e. an automorphism different from
    the idential one.

    Parameter
    ---------
    G : a simple graph

    Returns
    -------
    A CNF formula which is satiafiable if and only if graph G has a
    nontrivial automorphism.
    """
    description = "Graph automorphism formula for " + G.name
    F = GraphIsomorphism(G, G)
    F.header['description'] = description

    var = _graph_isomorphism_var

    F.add_clause([(False, var(u, u)) for u in enumerate_vertices(G)],
                 strict=True)

    return F
