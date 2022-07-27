#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Graph isomorphimsm/automorphism formulas
"""
from itertools import combinations
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph

def GraphIsomorphism(G1, G2, nontrivial=False, formula_class=CNF):
    """Graph Isomorphism formula

    The formula is the CNF encoding of the statement that two simple
    graphs G1 and G2 are isomorphic.

    Parameters
    ----------
    G1 : networkx.Graph
        an undirected graph object
    G2 : networkx.Graph
        an undirected graph object
    nontrivial: bool
        forbid identical mapping

    Returns
    -------
    A CNF formula which is satiafiable if and only if graphs G1 and G2
    are isomorphic.

    """
    G1 = Graph.normalize(G1, 'G1')
    G2 = Graph.normalize(G2, 'G2')

    description = "Graph isomorphism between (1) '{}' and (2) '{}'"
    description = description.format(G1.name, G2.name)

    F = formula_class(description=description)

    f = F.new_mapping(G1.order(), G2.order(),
                      label='x_{{{},{}}}')

    F.force_complete_mapping(f)
    F.force_surjective_mapping(f)
    F.force_functional_mapping(f)
    F.force_injective_mapping(f)

    # Edge consistency
    for u1, u2 in combinations(f.domain(), 2):
        for v1, v2 in combinations(f.range(), 2):
            if G1.has_edge(u1, u2) != G2.has_edge(v1, v2):
                F.add_clause([-f(u1, v1), -f(u2,v2)])
                F.add_clause([-f(u1, v2), -f(u2,v1)])

    F._mapping = f
    return F


def GraphAutomorphism(G, formula_class=CNF):
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
    G = Graph.normalize(G, 'G')
    description = "Graph automorphism formula for " + G.name

    F = GraphIsomorphism(G, G, formula_class=formula_class)
    F.header['description'] = description

    f = F._mapping
    F.add_clause([-f(u, u) for u in f.domain()])

    return F
