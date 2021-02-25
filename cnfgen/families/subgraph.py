#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of formulas that check for subgraphs
"""

from cnfgen.cnf import CNF

from itertools import combinations
from itertools import product
from itertools import permutations
from cnfgen.graphs import enumerate_vertices

from math import log, ceil

from networkx import complete_graph
from networkx import empty_graph

from textwrap import dedent
from cnfgen.graphs import CompleteBipartiteGraph


def SubgraphFormula(graph, templates, symmetric=False):
    """Test whether a graph contains one of the templates.

    Given a graph :math:`G` and a sequence of template graphs
    :math:`H_1`, :math:`H_2`, ..., :math:`H_t`, the CNF formula claims
    that :math:`G` contains an isomorphic copy of at least one of the
    template graphs.

    E.g. when :math:`H_1` is the complete graph of :math:`k` vertices
    and it is the only template, the formula claims that :math:`G`
    contains a :math:`k`-clique.

    Parameters
    ----------
    graph : networkx.Graph
        a simple graph

    templates : list-like object
        a sequence of graphs.

    symmetric:
        all template graphs are symmetric wrt permutations of
        vertices. This allows some optimization in the search space of
        the assignments.

    induce:
        force the subgraph to be induced (i.e. no additional edges are allowed)


    Returns
    -------
    a CNF object

    """
    # One of the templates is chosen to be the subgraph
    if len(templates) == 0:
        return CNF(description="Empty formula")
    selectors = len(templates)
    if selectors <= 2:
        selectors -= 1

    # comment the formula accordingly
    if selectors > 1:
        description = "{} does not contains any of the {} possible subgraphs.".format(
            graph.name, len(templates))
    else:
        description = "{} does not contain any copy of {}.".format(
            graph.name, templates[0].name)
    F = CNF(description=description)

    if selectors > 1:
        for cls in F.equal_to_constraint(selectors, 1):
            F.add_clause(cls)

    # A subgraph is chosen
    N = graph.order()
    k = max([s.order() for s in templates])

    def var_name(i, j): return "S_{{{0},{1}}}".format(i, j)

    B = CompleteBipartiteGraph(k, N)
    VG = None
    if symmetric:
        mapping = F.unary_mapping(selectors+1, B,
                                  functional=True,
                                  injective=True,
                                  nondecreasing=True)
    else:
        mapping = F.unary_mapping(selectors+1, B,
                                  functional=True,
                                  injective=True,
                                  nondecreasing=False)

    m = mapping.variables()

    for cls in mapping.clauses():
        F.add_clause(cls)

    # The selectors choose a template subgraph.  A mapping must map
    # edges to edges and non-edges to non-edges for the active
    # template.

    if len(templates) == 1:

        activation_prefixes = [[]]

    elif len(templates) == 2:

        activation_prefixes = [[1], [-1]]

    else:
        activation_prefixes = [[v] for v in range(1, selectors+1)]

    # maps must preserve the structure of the template graph
    for i in range(len(templates)):

        k = templates[i].order()

        if symmetric:
            # Using non-decreasing map to represent a subset
            localmaps = product(combinations(list(range(1, k+1)), 2),
                                combinations(list(range(1, N+1)), 2))
        else:
            localmaps = product(combinations(list(range(1, k+1)), 2),
                                permutations(list(range(1, N+1)), 2))

        for (i1, i2), (j1, j2) in localmaps:

            # check if this mapping is compatible
            tedge = templates[i].has_edge(i1, i2)
            gedge = graph.has_edge(j1, j2)
            if tedge == gedge:
                continue

            # if it is not, add the corresponding
            F.add_clause(
                activation_prefixes[i] + [-m(i1, j1), -m(i2, j2)], update_variables=False)

    return F


def CliqueFormula(G, k, symmetric=True):
    """Test whether a graph has a k-clique.

    Given a graph :math:`G` and a non negative value :math:`k`, the
    CNF formula claims that :math:`G` contains a :math:`k`-clique.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size
    symmetric: bool
        symmetry breaking

    Returns
    -------
    a CNF object

    """
    F = SubgraphFormula(G, [complete_graph(k)], symmetric=symmetric)
    description = "{} does not contain any {}-clique.".format(G.name, k)
    F.header['description'] = description
    return F


def BinaryCliqueFormula(G, k):
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

    Returns
    -------
    a CNF object

    """
    description = "Binary {0}-clique formula".format(k)
    F = CNF(description=description)

    clauses_gen = F.binary_mapping(range(1, k + 1),
                                   G.nodes(),
                                   injective=True,
                                   nondecreasing=True)

    for v in clauses_gen.variables():
        F.add_variable(v)

    for c in clauses_gen.clauses():
        F.add_clause(c, strict=True)

    for (i1, i2), (v1, v2) in product(combinations(range(1, k + 1), 2),
                                      combinations(G.nodes(), 2)):

        if not G.has_edge(v1, v2):
            F.add_clause(clauses_gen.forbid_image(i1, v1) +
                         clauses_gen.forbid_image(i2, v2),
                         strict=True)

    return F


def RamseyWitnessFormula(G, k, s):
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

    Returns
    -------
    a CNF object

    """
    F = SubgraphFormula(G, [complete_graph(k), empty_graph(s)], symmetric=True)
    description = "{} does not contain {}-cliques nor {}-independent sets.".format(
        G.name, k, s)
    F.header['description'] = description
    return F
