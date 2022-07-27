#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the ordering principle formulas
"""

from itertools import combinations, permutations
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import Graph
from cnfgen.localtypes import non_negative_int


def OrderingPrinciple(size, total=False, smart=False, plant=False, knuth=0, formula_class=CNF):
    """Generates the clauses for ordering principle

    Arguments:
    - `size`  : size of the domain
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    - `plant` : allow a single element to be minimum (could make the formula SAT)
    - `knuth` : Donald Knuth variant of the formula ver. 2 or 3 (anything else suppress it)
    """
    non_negative_int(size, 'size')

    if total or smart:
        description = "Total ordering principle"
    else:
        description = "Ordering principle"

    if smart:
        description += " (compact representation)"

    if knuth in [2, 3]:
        description += " (Knuth variant {})".format(knuth)

    F = GraphOrderingPrinciple(Graph.complete_graph(size), total, smart,
                               plant, knuth, formula_class=formula_class)
    F.header['description'] = description
    return F


def GraphOrderingPrinciple(graph,
                           total=False,
                           smart=False,
                           plant=False,
                           knuth=0,
                           formula_class=CNF):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies `total`)
    - `plant` : allow last element to be minimum (and could make the formula SAT)
    - `knuth` : Don Knuth variants 2 or 3 of the formula (anything else suppress it)
    """
    # Describe the formula
    graph = Graph.normalize(graph, 'graph')

    if total or smart:
        description = "Total graph ordering principle"
    else:
        description = "Graph ordering principle"

    if smart:
        description += " (compact representation)"

    if knuth in [2, 3]:
        description += " (Knuth variant {})".format(knuth)

    description += " on " + graph.name

    gop = formula_class(description=description)

    # Fix the vertex order
    n = graph.number_of_vertices()
    V = range(1, n+1)

    # Add variables
    if smart:
        X = gop.new_combinations(n, 2, label='x_{{{}}}')
    else:
        X = gop.new_permutations(n, 2, label='x_{{{}}}')
    #
    # Non minimality axioms
    #

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    # Allow minimum on last vertex if 'plant' options.
    for v in V:

        if v == n and plant:
            continue

        if smart:
            clause = []
            for u in graph.neighbors(v):
                if u < v:
                    clause.append(X(u, v))
                else:
                    clause.append(-X(v, u))
        else:
            clause = [X(u, v) for u in graph.neighbors(v)]

        gop.add_clause(clause)

    #
    # Smart version just needs 1/3 of transitivity axioms
    #
    if smart:
        for (v1, v2, v3) in combinations(V, 3):
            gop.add_clause([ X(v1, v2),  X(v2, v3), -X(v1, v3)])
            gop.add_clause([-X(v1, v2), -X(v2, v3),  X(v1, v3)])
        return gop

    #
    # Transitivity axiom for the other versions
    #
    for (v1, v2, v3) in permutations(V, 3):

        # knuth variants will reduce the number of
        # transitivity axioms
        if knuth == 2 and ((v2 < v1) or (v2 < v3)):
            continue
        if knuth == 3 and ((v3 < v1) or (v3 < v2)):
            continue

        gop.add_clause([-X(v1, v2), -X(v2, v3),  X(v1, v3)])

    # Antisymmetry axioms (useless for 'smart' representation)
    for (v1, v2) in combinations(V, 2):
        gop.add_clause([-X(v1, v2), -X(v2, v1)])

    # Totality axioms (useless for 'smart' representation)
    if total:
        for (v1, v2) in combinations(V, 2):
            gop.add_clause([X(v1, v2), X(v2, v1)])

    return gop
