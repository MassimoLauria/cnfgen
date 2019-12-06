#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the ordering principle formulas
"""

from cnfformula.cnf import CNF

from cnfformula.graphs import enumerate_vertices,neighbors
from itertools import combinations,permutations

import networkx

def OrderingPrinciple(size,total=False,smart=False,plant=False,knuth=0):
    """Generates the clauses for ordering principle

    Arguments:
    - `size`  : size of the domain
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    - `plant` : allow a single element to be minimum (could make the formula SAT)
    - `knuth` : Donald Knuth variant of the formula ver. 2 or 3 (anything else suppress it)
    """

    return GraphOrderingPrinciple(networkx.complete_graph(size),total,smart,plant,knuth)


def varname(v1, v2):
    return 'x_{{{0},{1}}}'.format(v1,v2)

def GraphOrderingPrinciple(graph,total=False,smart=False,plant=False,knuth=0):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies `total`)
    - `plant` : allow last element to be minimum (and could make the formula SAT)
    - `knuth` : Don Knuth variants 2 or 3 of the formula (anything else suppress it)
    """
    gop = CNF()

    # Describe the formula
    if total or smart:
        name = "Total graph ordering principle"
    else:
        name = "Ordering principle"

    if smart:
        name = name + "(compact representation)"

    if hasattr(graph, 'name'):
        gop.header = name+"\n on graph "+graph.name+".\n\n"+gop.header
    else:
        gop.header = name+".\n\n"+gop.header


    # Fix the vertex order
    V = enumerate_vertices(graph)

    # Add variables
    iterator = combinations if smart else permutations
    for v1,v2 in iterator(V,2):
        gop.add_variable(varname(v1,v2))

    #
    # Non minimality axioms
    #

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    # Allow minimum on last vertex if 'plant' options.

    for med in range(len(V) - (plant and 1)):
        clause = []
        for lo in range(med):
            if graph.has_edge(V[med], V[lo]):
                clause += [(True, varname(V[lo], V[med]))]
        for hi in range(med+1, len(V)):
            if not graph.has_edge(V[med], V[hi]):
                continue
            elif smart:
                clause += [(False, varname(V[med], V[hi]))]
            else:
                clause += [(True, varname(V[hi], V[med]))]
        gop.add_clause(clause, strict=True)

    #
    # Transitivity axiom
    #

    if len(V) >= 3:
        if smart:
            # Optimized version if smart representation of totality is used
            for (v1, v2, v3) in combinations(V, 3):

                gop.add_clause([(True,  varname(v1, v2)),
                                (True,  varname(v2, v3)),
                                (False, varname(v1, v3))],
                               strict=True)
                
                gop.add_clause([(False, varname(v1, v2)),
                                (False, varname(v2, v3)),
                                (True,  varname(v1, v3))],
                               strict=True)

        elif total:
            # With totality we still need just two axiom per triangle
            for (v1, v2, v3) in combinations(V, 3):
                
                gop.add_clause([(False, varname(v1, v2)),
                                (False, varname(v2, v3)),
                                (False, varname(v3, v1))],
                               strict=True)

                gop.add_clause([(False, varname(v1, v3)),
                                (False, varname(v3, v2)),
                                (False, varname(v2, v1))],
                               strict=True)

        else:
            for (v1, v2, v3) in permutations(V, 3):

                # knuth variants will reduce the number of
                # transitivity axioms
                if knuth == 2 and ((v2 < v1) or (v2 < v3)):
                    continue
                if knuth == 3 and ((v3 < v1) or (v3 < v2)):
                    continue

                gop.add_clause([(False, varname(v1, v2)),
                                (False, varname(v2, v3)),
                                (True,  varname(v1, v3))],
                               strict=True)

    if not smart:
        # Antisymmetry axioms (useless for 'smart' representation)
        for (v1, v2) in combinations(V, 2):
            gop.add_clause([(False, varname(v1, v2)),
                            (False, varname(v2, v1))],
                           strict=True)

        # Totality axioms (useless for 'smart' representation)
        if total:
            for (v1, v2) in combinations(V, 2):
                gop.add_clause([(True, varname(v1, v2)),
                                (True, varname(v2, v1))],
                               strict=True)

    return gop
