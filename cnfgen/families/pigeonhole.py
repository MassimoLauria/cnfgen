#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from cnfgen.cnf import CNF
from cnfgen.graphs import bipartite_sets

from itertools import combinations, product


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

    >>> print(PigeonholePrinciple(4,3).dimacs(export_header=False))
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
    """
    def var_name(p, h):
        return 'p_{{{0},{1}}}'.format(p, h)

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
    php = CNF(description=description)

    if pigeons < 0 or holes < 0:
        raise ValueError(
            "Number of pigeons and holes must both be non negative")

    mapping = php.unary_mapping(range(1, pigeons + 1),
                                range(1, holes + 1),
                                var_name=var_name,
                                injective=True,
                                functional=functional,
                                surjective=onto)

    for v in mapping.variables():
        php.add_variable(v)

    for c in mapping.clauses():
        php.add_clause_unsafe(c)

    return php


def GraphPigeonholePrinciple(graph, functional=False, onto=False):
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

    Arguments:
    - `graph` : bipartite graph
    - `functional`: add clauses to enforce at most one edge per left vertex
    - `onto`: add clauses to enforce that any right vertex has one incident edge


    Remark: the graph vertices must have the 'bipartite' attribute
    set. Left vertices must have it set to 0 and the right ones to
    1. A KeyException is raised otherwise.

    """
    def var_name(p, h):
        return 'p_{{{0},{1}}}'.format(p, h)

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

    description = "{0} formula on {1}".format(formula_name, graph.name)
    gphp = CNF(description=description)

    Left, Right = bipartite_sets(graph)

    mapping = gphp.unary_mapping(Left,
                                 Right,
                                 sparsity_pattern=graph,
                                 var_name=var_name,
                                 injective=True,
                                 functional=functional,
                                 surjective=onto)

    for v in mapping.variables():
        gphp.add_variable(v)

    for c in mapping.clauses():
        gphp.add_clause_unsafe(c)

    return gphp


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

    description = "Binary Pigeonhole Principle for {0} pigeons and {1} holes".format(
        pigeons, holes)
    bphp = CNF(description=description)

    if pigeons < 0 or holes < 0:
        raise ValueError(
            "Number of pigeons and holes must both be non negative")

    bphpgen = bphp.binary_mapping(range(1, pigeons + 1),
                                  range(1, holes + 1),
                                  injective=True)

    for v in bphpgen.variables():
        bphp.add_variable(v)

    for c in bphpgen.clauses():
        bphp.add_clause_unsafe(c)

    return bphp


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
    rphp = CNF()
    rphp.header[
        'description'] = "Relativized pigeonhole principle formula for {0} pigeons, {1} resting places and {2} holes".format(
            pigeons, resting_places, holes)

    if pigeons < 0:
        raise ValueError('The number of pigeons must be non-negative')
    if resting_places < 0:
        raise ValueError('The number of resting places must be non-negative')
    if holes < 0:
        raise ValueError('The number of holes must be non-negative')

    def p(u, v):
        return 'p_{{{0},{1}}}'.format(u, v)

    def q(v, w):
        return 'q_{{{0},{1}}}'.format(v, w)

    def r(v):
        return 'r_{{{0}}}'.format(v)

    U = range(1, 1 + pigeons)
    V = range(1, 1 + resting_places)
    W = range(1, 1 + holes)
    for u, v in product(U, V):
        rphp.add_variable(p(u, v))
    for v, w in product(V, W):
        rphp.add_variable(q(v, w))
    for v in V:
        rphp.add_variable(r(v))

    # NOTE: the order of ranges in the products are chosen such that related clauses appear after each other

    # (3.1a) p[u,1] v p[u,2] v ... v p[u,n] for all u \in [k]
    # Each pigeon goes into a resting place
    for u in U:
        rphp.add_clause([(True, p(u, v)) for v in V], strict=True)
    # (3.1b) ~p[u,v] v ~p[u',v] for all u, u' \in [k], u != u', v \in [n]
    # no conflict on any resting place
    for (v, (u, u_)) in product(V, combinations(U, 2)):
        rphp.add_clause([(False, p(u, v)), (False, p(u_, v))], strict=True)
    # (3.1c) ~p[u,v] v r[v] for all u \in [k], v \in [n]
    # resting place activation
    for (v, u) in product(V, U):
        rphp.add_clause([(False, p(u, v)), (True, r(v))], strict=True)
    # (3.1d) ~r[v] v q[v,1] v ... v q[v,k-1] for all v \in [n]
    # pigeons leave the resting place
    for v in V:
        rphp.add_clause([(False, r(v))] + [(True, q(v, w)) for w in W],
                        strict=True)
    # (3.1e) ~r[v] v ~r[v'] v ~q[v,w] v ~q[v',w] for all v, v' \in [n], v != v', w \in [k-1]
    # no conflict on any hole, for two pigeons coming from two resting places
    for (w, (v, v_)) in product(W, combinations(V, 2)):
        rphp.add_clause([(False, r(v)), (False, r(v_)), (False, q(v, w)),
                         (False, q(v_, w))],
                        strict=True)

    return rphp
