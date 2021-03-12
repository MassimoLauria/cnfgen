#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from itertools import combinations, product

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import BaseBipartiteGraph,BipartiteGraph, CompleteBipartiteGraph
from cnfgen.localtypes import non_negative_int

def PigeonholePrinciple(pigeons, holes, functional=False, onto=False):
    """Pigeonhole Principle CNF formula

    The pigeonhole  principle claims  that no M  pigeons can sit  in N
    pigeonholes  without collision  if M>N.   The  counterpositive CNF
    formulation  requires  such mapping  to  be  satisfied. There  are
    different  variants of this  formula, depending  on the  values of
    `functional` and `onto` argument.

    - PHP: pigeon can sit in multiple holes
    - FPHP: each pigeon sits in exactly one hole
    - onto-PHP: pigeon can  sit in multiple holes, every  hole must be
                covered.
    - Matching: one-to-one bijection between pigeons and holes.

    Arguments:
    - `pigeon`: number of pigeons
    - `hole`:   number of holes
    - `functional`: add clauses to enforce at most one hole per pigeon
    - `onto`: add clauses to enforce that any hole must have a pigeon

    >>> print(PigeonholePrinciple(4,3).to_dimacs())
    p cnf 12 22
    1 2 3 0
    4 5 6 0
    7 8 9 0
    10 11 12 0
    -1 -4 0
    -1 -7 0
    -1 -10 0
    -4 -7 0
    -4 -10 0
    -7 -10 0
    -2 -5 0
    -2 -8 0
    -2 -11 0
    -5 -8 0
    -5 -11 0
    -8 -11 0
    -3 -6 0
    -3 -9 0
    -3 -12 0
    -6 -9 0
    -6 -12 0
    -9 -12 0
    <BLANKLINE>
    """
    non_negative_int(pigeons, 'pigeon')
    non_negative_int(holes, 'holes')

    if functional:
        if onto:
            formula_name = "Matching"
        else:
            formula_name = "Functional pigeonhole principle"
    else:
        if onto:
            formula_name = "Onto pigeonhole principle"
        else:
            formula_name = "Pigeonhole principle"

    description = "{0} formula for {1} pigeons and {2} holes".format(
        formula_name, pigeons, holes)
    F = CNF(description=description)

    p = F.new_mapping(pigeons, holes, label='p_{{{},{}}}')
    F.force_complete_mapping(p)

    if onto:
        F.force_surjective_mapping(p)

    F.force_injective_mapping(p)

    if functional:
        F.force_functional_mapping(p)

    return F


def GraphPigeonholePrinciple(G, functional=False, onto=False):
    """Graph Pigeonhole Principle CNF formula

    The graph pigeonhole principle CNF formula, defined on a bipartite
    graph G=(L,R,E), claims that there is a subset E' of the edges such that
    every vertex on the left size L has at least one incident edge in E' and
    every edge on the right side R has at most one incident edge in E'.

    This is possible only if the graph has a matching of size |L|.

    There are different variants of this formula, depending on the
    values of `functional` and `onto` argument.

    - PHP(G):  each left vertex can be incident to multiple edges in E'
    - FPHP(G): each left vertex must be incident to exaclty one edge in E'
    - onto-PHP: all right vertices must be incident to some vertex
    - matching: E' must be a perfect matching between L and R

    Parameters
    ----------
    G : cnfgen.graphs.BipartiteGraph
        the underlying bipartite
    functional: bool
        add clauses to enforce at most one edge per left vertex
    onto: bool
        add clauses to enforce that any right vertex has one incident edge
    """
    G = BipartiteGraph.normalize(G, 'G')
    if functional:
        if onto:
            formula_name = "Graph matching"
        else:
            formula_name = "Graph functional pigeonhole principle"
    else:
        if onto:
            formula_name = "Graph onto pigeonhole principle"
        else:
            formula_name = "Graph pigeonhole principle"

    description = "{0} formula on {1}".format(formula_name, G.name)
    F = CNF(description=description)

    if not isinstance(G, BaseBipartiteGraph):
        G = BipartiteGraph.from_networkx(G)


    if not G.is_bipartite():
        raise ValueError("The pattern graph must be bipartite")

    p = F.new_sparse_mapping(G, label='p_{{{},{}}}')
    F.force_complete_mapping(p)

    if onto:
        F.force_surjective_mapping(p)

    F.force_injective_mapping(p)

    if functional:
        F.force_functional_mapping(p)

    return F


def BinaryPigeonholePrinciple(pigeons, holes):
    """Binary Pigeonhole Principle CNF formula

    The pigeonhole principle claims that no M pigeons can sit in
    N pigeonholes without collision if M>N. This formula encodes the
    principle using binary strings to identify the holes.

    Parameters
    ----------
    pigeon : int
       number of pigeons
    holes : int
       number of holes
    """
    non_negative_int(pigeons, 'pigeon')
    non_negative_int(holes, 'holes')

    description = "Binary Pigeonhole Principle for {0} pigeons and {1} holes".format(
        pigeons, holes)
    F = CNF(description=description)

    p = F.new_binary_mapping(pigeons, holes)
    F.force_complete_mapping(p)
    F.force_injective_mapping(p)
    return F


def RelativizedPigeonholePrinciple(pigeons, resting_places, holes):
    """Relativized Pigeonhole Principle CNF formula

    The formula claims that pigeons can fly into holes with no
    conflicts, with the additional caveat that before landing in
    a hole, each pigeon stops in some resting place. No two pigeons
    can rest in the same place.

    A description can be found in [1]_

    Parameters
    ----------
    pigeons: int
        number of pigeons
    resting_places: int
        number of resting places
    holes: int
        number of holes

    References
    ----------
    .. [1] A. Atserias, M. Lauria and J. Nordström
           Narrow Proofs May Be Maximally Long
           IEEE Conference on Computational Complexity 2014

    """
    non_negative_int(pigeons, 'pigeon')
    non_negative_int(resting_places, 'resting_places')
    non_negative_int(holes, 'holes')

    rphp = CNF()
    rphp.header[
        'description'] = "Relativized pigeonhole principle formula for {0} pigeons, {1} resting places and {2} holes".format(
            pigeons, resting_places, holes)

    U = pigeons
    V = resting_places
    W = holes
    p = rphp.new_mapping(U, V, label='p_{{{0},{1}}}')
    q = rphp.new_mapping(V, W, label='q_{{{0},{1}}}')
    if V>0:
        r = rphp.new_block(V, label='r_{{{0}}}')

    # NOTE: the order of ranges in the products are chosen such that related clauses appear after each other

    # (3.1a) p[u,1] v p[u,2] v ... v p[u,n] for all u \in [k]
    # Each pigeon goes into a resting place
    for u in p.domain():
        rphp.add_clause(p(u,None))
    # (3.1b) ~p[u,v] v ~p[u',v] for all u, u' \in [k], u != u', v \in [n]
    # no conflict on any resting place
    for v in p.range():
        rphp.add_linear(p(None,v), '<=', 1)
    # (3.1c) ~p[u,v] v r[v] for all u \in [k], v \in [n]
    # resting place activation
    for (v, u) in product(p.range(), p.domain()):
        rphp.add_clause([-p(u, v), r(v)])
    # (3.1d) ~r[v] v q[v,1] v ... v q[v,k-1] for all v \in [n]
    # pigeons leave the resting place
    for v in q.domain():
        rphp.add_clause([-r(v)] + list(q(v, None)))
    # (3.1e) ~r[v] v ~r[v'] v ~q[v,w] v ~q[v',w] for all v, v' \in [n], v != v', w \in [k-1]
    # no conflict on any hole, for two pigeons coming from two resting places
    for (w, (v1, v2)) in product(q.range(), combinations(q.domain(), 2)):
        rphp.add_clause([-r(v1), -r(v2), -q(v1, w), -q(v2, w)])

    return rphp
