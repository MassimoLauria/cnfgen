#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode coloring related problems
"""

from cnfgen.cnf import CNF
from cnfgen.graphs import enumerate_vertices
from cnfgen.graphs import enumerate_edges
from cnfgen.graphs import neighbors

from itertools import combinations
from collections.abc import Iterable


def GraphColoringFormula(G, colors, functional=True):
    """Generates the clauses for colorability formula

    The formula encodes the fact that the graph :math:`G` has a coloring
    with color set ``colors``. This means that it is possible to
    assign one among the elements in ``colors``to that each vertex of
    the graph such that no two adjacent vertices get the same color.

    Parameters
    ----------
    G : networkx.Graph
        a simple undirected graph
    colors : list or positive int
        a list of colors or a number of colors

    Returns
    -------
    CNF
       the CNF encoding of the coloring problem on graph ``G``

    """
    if isinstance(colors, int) and colors >= 0:
        colors = list(range(1, colors + 1))

    if not isinstance(colors, Iterable):
        ValueError(
            "Parameter \"colors\" is expected to be a number or an iterable")

    # Describe the formula
    name = "Graph {}-Colorability".format(len(colors))

    if hasattr(G, 'name'):
        header = name + " of graph: " + G.name
    col = CNF(description=header)

    # Fix the vertex order
    V = enumerate_vertices(G)

    # Each vertex has a color
    for vertex in V:
        clause = []
        for color in colors:
            clause += [(True, 'x_{{{0},{1}}}'.format(vertex, color))]
        col.add_clause(clause)

        # unique color per vertex
        if functional:
            for (c1, c2) in combinations(colors, 2):
                col.add_clause([(False, 'x_{{{0},{1}}}'.format(vertex, c1)),
                                (False, 'x_{{{0},{1}}}'.format(vertex, c2))],
                               strict=True)

    # This is a legal coloring
    for (v1, v2) in enumerate_edges(G):
        for c in colors:
            col.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, c)),
                            (False, 'x_{{{0},{1}}}'.format(v2, c))],
                           strict=True)

    return col


def EvenColoringFormula(G):
    """Even coloring formula

    The formula is defined on a graph :math:`G` and claims that it is
    possible to split the edges of the graph in two parts, so that
    each vertex has an equal number of incident edges in each part.

    The formula is defined on graphs where all vertices have even
    degree. The formula is satisfiable only on those graphs with an
    even number of vertices in each connected component [1]_.

    Arguments
    ---------
    G : networkx.Graph 
       a simple undirected graph where all vertices have even degree

    Raises
    ------
    ValueError
       if the graph in input has a vertex with odd degree

    Returns
    -------
    CNF object

    References
    ----------
    .. [1] Locality and Hard SAT-instances, Klas Markstrom
       Journal on Satisfiability, Boolean Modeling and Computation 2 (2006) 221-228

    """
    description = "Even coloring formula on " + G.name
    F = CNF(description=description)

    def var_name(u, v):
        if u <= v:
            return 'x_{{{0},{1}}}'.format(u, v)
        else:
            return 'x_{{{0},{1}}}'.format(v, u)

    for (u, v) in enumerate_edges(G):
        F.add_variable(var_name(u, v))

    # Defined on both side
    for v in enumerate_vertices(G):

        if G.degree(v) % 2 == 1:
            raise ValueError(
                "Markstrom's Even Coloring formulas requires all vertices to have even degree."
            )

        edge_vars = [var_name(u, v) for u in neighbors(G, v)]

        for cls in CNF.equal_to_constraint(edge_vars, len(edge_vars) // 2):
            F.add_clause(cls, strict=True)

    return F
