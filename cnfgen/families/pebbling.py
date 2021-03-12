#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from itertools import product
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph
from cnfgen.graphs import DirectedGraph
from cnfgen.localtypes import non_negative_int



def _uniqify_list(seq):
    """Remove duplicates while maintaining the order.

    (due to Dave Kirby)

    Seen on https://www.peterbe.com/plog/uniqifiers-benchmark
    """
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def PebblingFormula(digraph):
    """Pebbling formula

    Build a pebbling formula from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    Arguments:
    - `digraph`: directed acyclic graph.
    """
    digraph = DirectedGraph.normalize(digraph, 'digraph')
    if not digraph.is_dag():
        raise ValueError(
            "'digraph' must be acyclic, and topologically sorted")

    description = 'Pebbling formula'
    description += " for " + digraph.name

    peb = CNF(description=description)
    x = peb.new_block(digraph.number_of_vertices(), label='x({})')

    for v in digraph.vertices():
        # If predecessors are pebbled the vertex must be pebbled
        peb.add_clause([-x(p) for p in digraph.predecessors(v)] + [x(v)])

        if digraph.out_degree(v) == 0:  #the sink
            peb.add_clause([-x(v)])

    return peb



def StoneFormula(D, nstones):
    """Stone formulas

    The stone formulas have been introduced in [2]_ and generalized in
    [1]_. They are one of the classic examples that separate regular
    resolutions from general resolution [1]_.

    A \"Stones formula\" from a directed acyclic graph :math:`D`
    claims that each vertex of the graph is associated with one on
    :math:`s` stones (not necessarily in an injective way).
    In particular for each vertex :math:`v` in :math:`V(D)` and each
    stone :math:`j` we have a variable :math:`P_{v,j}` that claims
    that stone :math:`j` is associated to vertex :math:`v`.

    Each stone can be either red or blue, and not both.
    The propositional variable :math:`R_j` if true when the stone
    :math:`j` is red and false otherwise.

    The clauses of the formula encode the following constraints.
    If a stone is on a source vertex (i.e. a vertex with no incoming
    edges), then it must be red. If all stones on the predecessors of
    a vertex are red, then the stone of the vertex itself must be red.

    The formula furthermore enforces that the stones on the sinks
    (i.e. vertices with no outgoing edges) are blue.

    Parameters
    ----------
    D : a directed acyclic graph
        it should be a directed acyclic graph.
    nstones : int
       the number of stones.

    Raises
    ------
    ValueError
       if :math:`D` is not a directed acyclic graph

    ValueError
       if the number of stones is negative

    References
    ----------
    .. [1] M. Alekhnovich, J. Johannsen, T. Pitassi and A. Urquhart
    	   An Exponential Separation between Regular and General Resolution.
           Theory of Computing (2007)
    .. [2] R. Raz and P. McKenzie
           Separation of the monotone NC hierarchy.
           Combinatorica (1999)

    """
    D = DirectedGraph.normalize(D, 'D')
    if not D.is_dag():
        raise ValueError(
            "'D' must be acyclic, and topologically sorted")

    non_negative_int(nstones, 'nstones')

    description = "Stone formula of {} with {} stones".format(D.name, nstones)
    B = CompleteBipartiteGraph(D.number_of_vertices(),nstones)
    F = SparseStoneFormula(D, B)
    F.header['description'] = description
    return F

def SparseStoneFormula(D, B):
    """Sparse Stone formulas

    This is a variant of the :py:func:`StoneFormula`. See that for
    a description of the formula. This variant is such that each
    vertex has only a small selection of which stone can go to that
    vertex. In particular which stones are allowed on each vertex is
    specified by a bipartite graph :math:`B` on which the left
    vertices represent the vertices of DAG :math:`D` and the right
    vertices are the stones.

    If a vertex of :math:`D` correspond to the left vertex :math:`v`
    in :math:`B`, then its neighbors describe which stones are allowed
    for it.

    The vertices in :math:`D` do not need to have the same name as the
    one on the left side of :math:`B`. It is only important that the
    number of vertices in :math:`D` is the same as the vertices in the
    left side of :math:`B`.

    In that case the element at position :math:`i` in the ordered
    sequence ``enumerate_vertices(D)`` corresponds to the element of
    rank :math:`i` in the sequence of left side vertices of
    :math:`B` according to the output of ``Left, Right =
    bipartite_sets(B)``.

    Standard :py:func:`StoneFormula` is essentially equivalent to
    a sparse stone formula where :math:`B` is the complete graph.

    Parameters
    ----------
    D : a directed acyclic graph
        it should be a directed acyclic graph.
    B : bipartite graph

    Raises
    ------
    ValueError
       if :math:`D` is not a directed acyclic graph

    ValueError
       if :math:`B` is not a bipartite graph

    ValueError
       when size differs between :math:`D` and the left side of
       :math:`B`

    See Also
    --------
    StoneFormula

    """
    D = DirectedGraph.normalize(D, 'D')
    B = BipartiteGraph.normalize(B, 'B')
    if not D.is_dag():
        raise ValueError(
            "'D' must be acyclic, and topologically sorted")

    Left, stones = B.parts()

    if len(Left) != D.number_of_vertices():
        raise ValueError(
            "Formula requires the bipartite left side to match #vertices of the DAG."
        )

    description = "Sparse stone formula of {} with {} stones".format(D.name, len(stones))
    F = CNF(description=description)

    # Add variables in the appropriate order
    R = F.new_block(len(stones), label='R_{{{0}}}')  # a stone j is red

    # mapping from vertices to stones
    P = F.new_sparse_mapping(B, label='P_{{{0},{1}}}')
    F.force_complete_mapping(P)

    # If predecessors have red stones, the sink must have a red stone
    for v in D.vertices():
        for j in B.right_neighbors(v):
            pred = list(D.predecessors(v))
            stone_patterns = product(*tuple([s for s in
                                             B.right_neighbors(p) if s != j] for p in pred))
            for pattern in stone_patterns:
                F.add_clause([-P(p, s) for (p, s) in zip(pred, pattern)] +
                             [-P(v, j)] +
                             [-R(s) for s in _uniqify_list(pattern)] +
                             [R(j)])

        if D.out_degree(v) == 0:  #the sink
            for j in B.right_neighbors(v):
                F.add_clause([-P(v, j), -R(j)])

    return F
