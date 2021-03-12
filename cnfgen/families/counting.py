#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas
"""

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph


def CountingPrinciple(M, p):
    """Generates the clauses for the counting matching principle.

    The principle claims that there is a way to partition M in sets of
    size p each.

    Arguments:
    - `M`  : size of the domain
    - `p`  : size of each class

    """
    try:
        M+0
        p+0
    except TypeError:
        raise TypeError('M and p must be integers')

    if M < p or M < 1 or p < 1:
        raise ValueError(
            "M,p mustbe so that 1 <= p <= M")
    description = "Counting Principle: {0} divided in parts of size {1}.".format(
        M, p)
    F = CNF(description=description)

    def var_name(tpl):
        return "Y_{{" + ",".join("{0}".format(v) for v in tpl) + "}}"

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
    G = Graph.normalize(G)

    description = "Perfect Matching Principle on {}".format(G.name)
    F = CNF(description=description)
    e = F.new_graph_edges(G, label='e_{{{0},{1}}}')

    # Each vertex has exactly one edge set to one.
    for u in G.vertices():

        F.add_linear(e(u, None), '==', 1)

    return F
