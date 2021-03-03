#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of formulas that check for subgraphs
"""

import networkx as nx

from itertools import combinations
from itertools import product
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph

def SubgraphFormula(G, H, induced=False, symbreak=False):
    """Test whether a graph has a k-clique.

    Given two graphs :math:`H` and :math:`G`, the
    CNF formula claims that :math:`H` is an (induced) subgraph of :math:`G`.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    H : networkx.Graph
        the candidate subgraph
    induced: bool
        test for induced containment
    symbreak: bool
        force mapping to be non decreasing
        (this makes sense only if :math:`T` is symmetric)

    Returns
    -------
    a CNF object

    """
    F = CNF()
    if induced:
        description = "{} is not an induced subgraph of {}".format(H.name, G.name)
    else:
        description = "{} is not a subgraph of {}".format(H.name, G.name)
    F.header['description'] = description

    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)

    if isinstance(H, nx.Graph) and not isinstance(H, Graph):
        H = Graph.from_networkx(H)

    N = G.order()
    k = H.order()
    s = F.new_mapping(k, N, label='s_{{{},{}}}')
    F.force_complete_mapping(s)
    F.force_functional_mapping(s)
    F.force_injective_mapping(s)

    # Local consistency
    localmaps = product(combinations(list(range(1, k+1)), 2),
                        combinations(list(range(1, N+1)), 2))

    for (i1, i2), (j1, j2) in localmaps:

        # check if this mapping is compatible
        gedge = G.has_edge(j1, j2)
        tedge = H.has_edge(i1, i2)

        consistent = (gedge == tedge) or (gedge and not induced)

        if not consistent:
            F.add_clause([-s(i1, j1), -s(i2, j2)])
            F.add_clause([-s(i1, j2), -s(i2, j1)])
        elif symbreak:
            F.add_clause([-s(i1, j2), -s(i2, j1)])
    return F


def CliqueFormula(G, k, symbreak=True):
    """Test whether a graph has a k-clique.

    Given a graph :math:`G` and a non negative value :math:`k`, the
    CNF formula claims that :math:`G` contains a :math:`k`-clique.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size
    symbreak: bool
        force mapping to be non decreasing

    Returns
    -------
    a CNF object

    """
    F = CNF()
    description = "{} does not contain any {}-clique.".format(G.name, k)
    F.header['description'] = description

    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)

    N = G.order()
    s = F.new_mapping(k, N, label='s_{{{},{}}}')
    F.force_complete_mapping(s)
    F.force_functional_mapping(s)
    F.force_injective_mapping(s)

    # Local consistency
    localmaps = product(combinations(list(range(1, k+1)), 2),
                        combinations(list(range(1, N+1)), 2))

    for (i1, i2), (j1, j2) in localmaps:

        # check if this mapping is compatible
        edge = G.has_edge(j1, j2)
        if not edge:
            F.add_clause([-s(i1, j1), -s(i2, j2)])
            F.add_clause([-s(i1, j2), -s(i2, j1)])
        elif symbreak:
            F.add_clause([-s(i1, j2), -s(i2, j1)])
    return F


def BinaryCliqueFormula(G, k, symbreak=True):
    """Test whether a graph has a k-clique (binary encoding)

    Given a graph :math:`G` and a non negative value :math:`k`, the
    CNF formula claims that :math:`G` contains a :math:`k`-clique.
    This formula uses the binary encoding, in the sense that the
    clique elements are indexed by strings of bits.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size
    symbreak: bool
        force mapping to be non decreasing

    Returns
    -------
    a CNF object

    """
    F = CNF()
    description = "{} does not contain any {}-clique (Binary encoding).".format(G.name, k)
    F.header['description'] = description

    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)
    N = G.order()
    m = F.new_binary_mapping(k, N, label='y_{{{},{}}}')
    F.force_complete_mapping(m)
    F.force_injective_mapping(m)

    # Local consistency
    localmaps = product(combinations(list(range(1, k+1)), 2),
                        combinations(range(N), 2))

    for (i1, i2), (j1, j2) in localmaps:

        # check if this mapping is compatible
        edge = G.has_edge(j1, j2)
        if not edge:
            F.add_clause(m.forbid(i1, j1) + m.forbid(i2, j2))
            F.add_clause(m.forbid(i1, j2) + m.forbid(i2, j1))
        elif symbreak:
            F.add_clause(m.forbid(i1, j2) + m.forbid(i2, j1))
    return F


def RamseyWitnessFormula(G, k, s, symbreak=True):
    """True if graph contains either k-clique or and s independent set

    Given a graph :math:`G` and a non negative values :math:`k` and
    :math:`s`, the CNF formula claims that :math:`G` contains
    a neither a :math:`k`-clique nor an independet set of size
    :math:`s`.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size
    s : a non negative integer
        independet set size
    symbreak: bool
        force mapping to be non decreasing

    Returns
    -------
    a CNF object
    """
    F = CNF()
    description = "{} does not contain {}-cliques nor {}-independent sets.".format(
        G.name, k, s)
    F.header['description'] = description
    maybeclique = F.new_variable('C')

    if isinstance(G, nx.Graph) and not isinstance(G, Graph):
        G = Graph.from_networkx(G)
    N = G.order()
    s = F.new_mapping(k, N, label='s_{{{},{}}}')
    F.force_complete_mapping(s)
    F.force_functional_mapping(s)
    F.force_injective_mapping(s)

    # Local consistency
    localmaps = product(combinations(range(1,k+1), 2),
                        combinations(range(1,N+1), 2))

    for (i1, i2), (j1, j2) in localmaps:

        # check if this mapping is compatible
        edge = G.has_edge(j1, j2)
        # increasing map
        if not edge:
            F.add_clause([-maybeclique, -s(i1, j1), -s(i2, j2)])
        else:
            F.add_clause([maybeclique, -s(i1, j1), -s(i2, j2)])
        # decreasing map
        if symbreak:
            F.add_clause([-s(i1, j2), -s(i2, j1)])
        elif not edge:
            F.add_clause([-maybeclique, -s(i1, j2), -s(i2, j1)])
        else:
            F.add_clause([maybeclique, -s(i1, j2), -s(i2, j1)])
    return F
