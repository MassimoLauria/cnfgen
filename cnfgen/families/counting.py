#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas
"""

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph
from cnfgen.localtypes import positive_int, non_negative_int


def CountingPrinciple(M, p):
    """Counting principle

    The principle claims that there is a way to partition M elements
    in sets of size p each.

    Parameters
    ----------
    M : non negative integer
        size of the domain
    p : positive integer
        size of each part

    Returns
    -------
    cnfgen.CNF
    """
    non_negative_int(M, "M")
    positive_int(p, "p")

    description = "Counting Principle: {0} divided in parts of size {1}.".format(
        M, p)
    F = CNF(description=description)

    X = F.new_combinations(M, p)

    stars = [[] for i in range(M)]
    for pattern, var in zip(X.indices(), X()):
        for i in pattern:
            stars[i-1].append(var)

    # Each element of the domain is in exactly one part.
    for star in stars:
        F.add_linear(star, '==', 1)

    return F


def PerfectMatchingPrinciple(G):
    """Generates the clauses for the graph perfect matching principle.

    The principle claims that there is a way to select edges to such
    that all vertices have exactly one incident edge set to 1.

    Parameters
    ----------
    G : undirected graph

    """
    # Describe the formula
    G = Graph.normalize(G, 'G')

    description = "Perfect Matching Principle on {}".format(G.name)
    F = CNF(description=description)
    e = F.new_graph_edges(G, label='e_{{{0},{1}}}')

    # Each vertex has exactly one edge set to one.
    for u in G.vertices():

        F.add_linear(e(u, None), '==', 1)

    return F
