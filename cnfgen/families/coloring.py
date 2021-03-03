#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode coloring related problems
"""
import networkx as nx

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph

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
    colors : non negative int
        the number of colors

    Returns
    -------
    CNF
       the CNF encoding of the coloring problem on graph ``G``

    """
    if colors < 0:
        ValueError(
            "Parameter \"colors\" is expected to be a non negative")

    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)

    # Describe the formula
    description = "Graph {}-Colorability of {}".format(colors,G)
    F = CNF(description=description)
    col = F.new_mapping(G.order(), colors,label='x_{{{0}{1}}}')

    # Color each vertex
    F.force_complete_mapping(col)
    F.force_functional_mapping(col)


    # This is a legal coloring
    for (v1, v2) in G.edges():
        for c in range(1,colors+1):
            F.add_clause([-col(v1, c), -col(v2, c)])

    return F


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
    G : cnfgen.graphs.Graph
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
    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)

    description = "Even coloring formula on " + G.name
    F = CNF(description=description)

    e = F.new_graph_edges(G)

    # Defined on both side
    for v in G.nodes():

        if G.degree(v) % 2 == 1:
            raise ValueError(
                "Markstrom's Even Coloring formulas requires all\nvertices to have even degree."
            )

        edge_vars = [e(u, v) for u,v in e.indices(v,None)]

        F.add_linear(edge_vars,'==', len(edge_vars) // 2)
    return F
