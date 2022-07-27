#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Pigeonhole principle formulas

The pigeonhole principle :math:`\\mathsf{PHP}_{n}^{m}`, written in
conjunctive normal form, is a propositional formula which claims that
it is possible to place :math:`m` pigeons into :math:`n` holes without
collisions, whenever :math:`m > n`.

Pigeonhole principle formulas are classic benchmarks for SAT solving
and for Resolution proof systems. The module contains the
implementation of several variants of this formulas.

The most classic pigeonhole principle formula
:math:`\\mathsf{PHP}_{n}^{n+1}` was the first CNF proved to be hard
for resolution [H85]_.

.. [H85] Haken, A. (1985). The intractability of resolution.
         Theoretical Computer Science, 39, 297–308.
"""

from itertools import combinations, product

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import BaseBipartiteGraph, BipartiteGraph
from cnfgen.localtypes import non_negative_int


def PigeonholePrinciple(pigeons, holes, functional=False, onto=False):
    """Pigeonhole Principle CNF formula

    The pigeonhole principle CNF formula claims that that it is
    possibile to place :math:`m` pigeons into :math:`n` holes without
    collisions. This is clearly impossible whenever :math:`m > n`.

    The formula is encoded with variables :math:`p_{i,j}` for :math:`i
    \\in [m]` and :math:`j \\in [n]` where the intended meaning is
    that :math:`p_{i,j}` is `True` when pigeon :math:`i` flies into
    hole :math:`j`. There are different variants of this formula,
    depending on the values of `functional` and `onto` argument.

    - PHP: pigeon can sit in multiple holes
    - FPHP: each pigeon sits in exactly one hole
    - onto-PHP: pigeon can  sit in multiple holes, every  hole must be covered
    - Matching: one-to-one bijection between pigeons and holes.

    Parameters
    ----------
    pigeon: int
        number of pigeons (must be >=0).
    hole: int
        number of holes (must be >=0).
    functional: bool, optional
        enforce at most one hole per pigeon (default: False).
    onto: bool, optional
        enforce that any hole must have a pigeon (default: False).

    Returns
    -------
    :py:class:`cnfgen.formula.cnf.CNF`
         A CNF formulas encoding the pigeonhole principle.

    Raises
    ------
    TypeError
        If either `pigeons` or `holes` is not an integer number.
    ValueError
        If either `pigeons` or `holes` is less than zero.

    Examples
    --------
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
    graph :math:`G=(L,R,E)`, is a variant of the pigeonhole principle
    where the left vertices :math:`L` are the pigeons, the right
    vertices :math:`R` are the holes. The formula claims that there is
    a subset of edges :math:`E' \\subseteq E` such that every vertex in
    :math:`u \\in L` has at least one incident edge in :math:`E'` and every
    :math:`v \\in R` has at most one incident edge in :math:`E'`.

    The formula is satisfiable if and only if the graph has a matching
    of size :math:`|L|`.

    The formula is encoded with variables :math:`p_{u,v}` for :math:`u
    \\in L` and :math:`v \\in R` where the intended meaning is
    that :math:`p_{u,v}` is `True` when pigeon :math:`u` flies into
    hole :math:`v`. There are different variants of this formula,
    depending on the values of `functional` and `onto` argument.

    - PHP(G):  each :math:`u \\in L` can fly to multiple :math:`v \\in R`
    - FPHP(G): each :math:`u \\in L` can fly to exactly one :math:`v \\in R`
    - onto-PHP: each :math:`v \\in R` must get a pigeon
    - matching: :math:`E'` must be a perfect matching

    Parameter `G` can be either of type
    :py:class:`cnfgen.graphs.BipartiteGraph` or of type
    a :py:class:`networkx.graph`. In the latter case it must be
    a correct representation of a bipartite graph according to
    [NetworkX]_.

    Parameters
    ----------
    G : :py:class:`cnfgen.graphs.BipartiteGraph` or :py:class:`networkx.graph`
        the bipartite graph describing the possible pairings
    functional: bool
        enforce at most one edge per left vertex
    onto: bool
        enforce that any right vertex has one incident edge

    Returns
    -------
    :py:class:`cnfgen.formula.cnf.CNF`
         A CNF formulas encoding the graph pigeonhole principle.

    Raises
    ------
    TypeError
        `G` is neither a :py:class:`cnfgen.graphs.BipartiteGraph` nor a :py:class:`networkx.graph`
    ValueError
        `G` is not a proper bipartite graph

    References
    ----------
    [Networkx] https://networkx.org/documentation/networkx-2.5/reference/algorithms/generated/networkx.algorithms.bipartite.basic.is_bipartite.html

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

    The binary pigeonhole principle CNF formula claims that that it is
    possibile to place :math:`m` pigeons into :math:`n` holes without
    collisions. This is clearly impossible whenever :math:`m > n`.

    This formula encodes the principle using binary strings to
    identify the holes. Let :math:`b` the smallest number of bits
    sufficient to encode in binary all values from :math:`0` to
    :math:`n-1`. For every :math:`i \\in [m]` there are :math:`b`
    dedicated boolean variables encoding the hole where the pigeon
    :math:`i` flies.

    Parameters
    ----------
    pigeon: int
        number of pigeons (must be >=0).
    hole: int
        number of holes (must be >=0).

    Returns
    -------
    :py:class:`cnfgen.formula.cnf.CNF`
         A CNF formulas encoding binary the pigeonhole principle.

    Raises
    ------
    TypeError
        If either `pigeons` or `holes` is not an integer number.
    ValueError
        If either `pigeons` or `holes` is less than zero.
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

    This formula is a variant of the pigeonhole principle. We consider
    :math:`m` pigeons, :math:`r` resting places, and :math:`n` holes.
    The formula claims that pigeons can fly into holes with no
    conflicts, with the additional caveat that before landing in
    a hole, each pigeon stops in some resting place. No two pigeons
    can rest in the same place.

    The formula is encoded with variables :math:`p_{i,j}` for :math:`i
    \\in [m]` and :math:`k \\in [t]`, and variables :math:`q_{k,j}`
    for :math:`k \\in [t]` and :math:`j \\in [n]`. The intended
    meaning is that :math:`p_{i,k}` is `True` when pigeon :math:`i`
    rests into a resting place :math:`k`, and :math:`q_{k,j}` is
    `True` when the pigeon resting at :math:`k` flies into hole
    :math:`j`. The formula is only satisfiable when :math:`m \\leq
    t \\leq n`.

    A more complete description of the formula can be found in
    [ALN16]_

    Parameters
    ----------
    pigeons: int
        number of pigeons (must be >=0).
    resting_places: int
        number of resting places (must be >=0).
    holes: int
        number of holes (must be >=0).

    Returns
    -------
    :py:class:`cnfgen.formula.cnf.CNF`
         A CNF formulas encoding the pigeonhole principle.

    Raises
    ------
    TypeError
        If either `pigeons`, `resting_places`, or `holes` is not an integer
        number.
    ValueError
        If either `pigeons`, `resting_places`, or `holes` is less than zero.

    References
    ----------
    .. [ALN16] Atserias, A., Lauria, M., & Nordstr\"om, Jakob (2016).
               Narrow Proofs May Be Maximally Long. ACM Transactions on
               Computational Logic, 17(3), 19–1–19–30.
               http://dx.doi.org/10.1145/2898435

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
    if V > 0:
        r = rphp.new_block(V, label='r_{{{0}}}')

    # NOTE: the order of ranges in the products are chosen such that related clauses appear after each other

    # (3.1a) p[u,1] v p[u,2] v ... v p[u,n] for all u \in [k]
    # Each pigeon goes into a resting place
    for u in p.domain():
        rphp.add_clause(p(u,None))
    # (3.1b) ~p[u,v] v ~p[u',v] for all u, u' \in [k], u != u', v \in [n]
    # no conflict on any resting place
    for v in p.range():
        rphp.cardinality_leq(p(None,v), 1)
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
