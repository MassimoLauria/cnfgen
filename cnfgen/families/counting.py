#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas
"""

from cnfgen.cnf import CNF
from cnfgen.graphs import enumerate_vertices
from cnfgen.graphs import neighbors

from itertools import combinations


def CountingPrinciple(M, p):
    """Generates the clauses for the counting matching principle.
    
    The principle claims that there is a way to partition M in sets of
    size p each.

    Arguments:
    - `M`  : size of the domain
    - `p`  : size of each class

    """
    if M < p:
        raise ValueError(
            "Domain size must be larger or equal than the class size")
    description = "Counting Principle: {0} divided in parts of size {1}.".format(
        M, p)
    cnf = CNF(description=description)

    def var_name(tpl):
        return "Y_{{" + ",".join("{0}".format(v) for v in tpl) + "}}"

    # Incidence lists
    incidence = [[] for _ in range(M)]
    for tpl in combinations(range(M), p):
        for i in tpl:
            incidence[i].append(tpl)

    # Each element of the domain is in exactly one part.
    for el in range(M):

        edge_vars = [var_name(tpl) for tpl in incidence[el]]

        for cls in CNF.equal_to_constraint(edge_vars, 1):
            cnf.add_clause(cls)

    return cnf


def PerfectMatchingPrinciple(G):
    """Generates the clauses for the graph perfect matching principle.
    
    The principle claims that there is a way to select edges to such
    that all vertices have exactly one incident edge set to 1.

    Parameters
    ----------
    G : undirected graph

    """
    # Describe the formula
    description = "Perfect Matching Principle"

    if hasattr(G, 'name'):
        description += " on " + G.name

    cnf = CNF(description=description)

    def var_name(u, v):
        if u <= v:
            return 'x_{{{0},{1}}}'.format(u, v)
        else:
            return 'x_{{{0},{1}}}'.format(v, u)

    # Each vertex has exactly one edge set to one.
    for v in enumerate_vertices(G):

        edge_vars = [var_name(u, v) for u in neighbors(G, v)]

        for cls in CNF.equal_to_constraint(edge_vars, 1):
            cnf.add_clause(cls)

    return cnf
