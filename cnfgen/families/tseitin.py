#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Tseitin formulas
"""
import networkx as nx
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph


def TseitinFormula(G, charges=None):
    """Build a Tseitin formula based on the input graph.

    Odd charge is put on the first vertex by default, unless other
    vertices are is specified in input.

    Arguments:
    - G: cnfgen.graphs.Graph
    - `charges': odd or even charge for each vertex
    """
    G = Graph.normalize(G)

    n = G.order()
    parity = None

    if charges is None:
        charges = [1] + [0] * (n - 1)  # odd charge on first vertex
        parity = 'odd'
    else:
        parity = 'even' if sum(charges) % 2 == 0 else 'odd'
        charges = [bool(c) for c in charges]  # map to boolean

    if len(charges) < G.order():
        charges = charges + [0] * (n - len(charges))  # pad with even charges

    # init formula
    description = "Tseitin formula on {0}, with {1} charge".format(
        G.name, parity)
    tse = CNF(description=description)
    e = tse.new_graph_edges(G,label="E_{{{0},{1}}}")

    # add constraints
    for v, c in zip(G.vertices(), charges):
        tse.add_parity([e(u, v) for u in G.neighbors(v)], c)

    return tse
