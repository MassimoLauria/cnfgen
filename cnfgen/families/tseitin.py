#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Tseitin formulas
"""
import networkx as nx
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph


def TseitinFormula(G, charges=None, formula_class=CNF):
    """Build a Tseitin formula based on the input graph.

    By default, an odd charge is put on the first vertex, unless
    another pattern of charges are specified. The pattern is specified
    via a sequence of boolean values in the `charges` variable (True
    means odd). If the sequence is shorter than the sequence of
    vertices, it is padded with Falses. If it is longer, excessive
    values will be ignored. Any non-boolean value in `charges` is
    interpreted as boolean via `bool` cast.

    Parameters
    ----------
    G : cnfgen.Graph or networkx.Graph

    charges: a sequence of boolean
    """
    G = Graph.normalize(G,'G')

    n = G.order()
    parity = None

    if charges is None:
        charges = [True] + [False] * (n - 1)  # odd charge on first vertex
        parity = 'odd'
    else:
        parity = 'even' if sum(charges) % 2 == 0 else 'odd'
        charges = [bool(c) for c in charges]  # map to boolean

    if len(charges) < G.order():
        charges = charges + [False] * (n - len(charges))  # pad with even charges

    # init formula
    description = "Tseitin formula on {0}, with {1} charge".format(
        G.name, parity)
    tse = formula_class(description=description)
    e = tse.new_graph_edges(G, label="E_{{{0},{1}}}")

    # add constraints
    for v, c in zip(G.vertices(), charges):
        tse.add_parity([e(u, v) for u in G.neighbors(v)], c)

    return tse
