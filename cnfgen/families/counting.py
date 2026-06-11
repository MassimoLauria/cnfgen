#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas
"""

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph, BipartiteGraph
from cnfgen.localtypes import positive_int, non_negative_int


def CountingPrinciple(M, p, formula_class=CNF):
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
    F = formula_class(description=description)

    X = F.new_combinations(M, p)

    stars = [[] for i in range(M)]
    for pattern, var in zip(X.indices(), X()):
        for i in pattern:
            stars[i-1].append(var)

    # Each element of the domain is in exactly one part.
    for star in stars:
        F.cardinality_eq(star,  1)

    return F


def PerfectMatchingPrinciple(G, formula_class=CNF):
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
    F = formula_class(description=description)
    e = F.new_graph_edges(G, label='e_{{{0},{1}}}')

    # Each vertex has exactly one edge set to one.
    for u in G.vertices():

        F.cardinality_eq(e(u, None),  1)

    return F


def MutilatedChessboard(W, H, formula_class=CNF):
    """Generates the clauses for the mutilated chessboard formula

    The principle claims that there is a perfect matching on a WxH
    grid from which the top left and botton right corner have
    been removed. We assume H>1 and W>1.

    The formula is satisfiable only when the height + width is an
    odd number.

    Parameters
    ----------
    W : width of the grid
    H : height of the grid

    """
    if not isinstance(W, int) or not isinstance(H, int):
        raise TypeError("W and H must be of int type")

    if W < 2 or H < 2:
        raise ValueError("W and H must be >= 2")

    G = Graph(W * H - 2)   # W*H verices minus two corners

    def v(r, c):
        return r * W + c   # vertices id start from 1

    for r in range(H):
        for c in range(W):
            if r == 0 and c == 0:  # top left corner
                continue
            if r == H - 1 and c >= W - 2:  # bottom right corner or its left neighbor
                continue
            if r >= H - 2 and c == W - 1:  # bottom right corner or its top  neighbors
                continue
            if c < W - 1:
                G.add_edge(v(r, c), v(r, c + 1))  # edges toward right
            if r < H - 1:
                G.add_edge(v(r, c), v(r + 1, c))  # edges toward bottom

    description = f"Mutilated Chessboard {W}x{H}"
    F = formula_class(description=description)
    e = F.new_graph_edges(G, label="e_{{{0},{1}}}")

    # Each vertex has exactly one edge set to one.
    for u in G.vertices():
        F.cardinality_eq(e(u, None), 1)

    return F
