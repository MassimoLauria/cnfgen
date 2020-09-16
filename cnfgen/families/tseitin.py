#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Tseitin formulas
"""

from cnfgen.cnf import CNF
from cnfgen.graphs import enumerate_vertices, neighbors


def TseitinFormula(graph, charges=None):
    """Build a Tseitin formula based on the input graph.

    Odd charge is put on the first vertex by default, unless other
    vertices are is specified in input.

    Arguments:
    - `graph`: input graph
    - `charges': odd or even charge for each vertex
    """
    V = enumerate_vertices(graph)
    parity = None

    if charges is None:
        charges = [1] + [0] * (len(V) - 1)  # odd charge on first vertex
        parity = 'odd'
    else:
        parity = 'even' if sum(charges) % 2 == 0 else 'odd'
        charges = [bool(c) for c in charges]  # map to boolean

    if len(charges) < len(V):
        charges = charges + [0] * (len(V) - len(charges)
                                   )  # pad with even charges

    # init formula
    description = "Tseitin formula on {0}, with {1} charge".format(
        graph.name, parity)
    tse = CNF(description=description)
    edgename = {}

    for (u, v) in sorted(graph.edges(), key=sorted):
        edgename[(u, v)] = "E_{{{0},{1}}}".format(u, v)
        edgename[(v, u)] = "E_{{{0},{1}}}".format(u, v)
        tse.add_variable(edgename[(u, v)])

    # add constraints
    for v, c in zip(V, charges):

        # produce all clauses and save half of them
        names = [edgename[(u, v)] for u in neighbors(graph, v)]
        for cls in CNF.parity_constraint(names, c):
            tse.add_clause(list(cls), strict=True)

    return tse
