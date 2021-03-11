#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of subset cardinality formulas
"""
from math import ceil, floor

from cnfgen.formula.cnf import CNF
from cnfgen.graphs import BipartiteGraph


def SubsetCardinalityFormula(B, equalities=False):
    r"""SubsetCardinalityFormula

    Consider a bipartite graph :math:`B`. The CNF claims that at least half
    of the edges incident to each of the vertices on left side of :math:`B`
    must be zero, while at least half of the edges incident to each
    vertex on the left side must be one.

    Variants of these formula on specific families of bipartite graphs
    have been studied in [1]_, [2]_ and [3]_, and turned out to be
    difficult for resolution based SAT-solvers.

    Each variable of the formula is denoted as :math:`x_{i,j}` where
    :math:`\{i,j\}` is an edge of the bipartite graph. The clauses of
    the CNF encode the following constraints on the edge variables.

    For every left vertex i with neighborhood :math:`\Gamma(i)`

    .. math::

         \sum_{j \in \Gamma(i)} x_{i,j} \geq \frac{|\Gamma(i)|}{2}

    For every right vertex j with neighborhood :math:`\Gamma(j)`

    .. math::

         \sum_{i \in \Gamma(j)} x_{i,j} \leq \frac{|\Gamma(j)|}{2}.

    If the ``equalities`` flag is true, the constraints are instead
    represented by equations.

    .. math::

         \sum_{j \in \Gamma(i)} x_{i,j} = \left\lceil \frac{|\Gamma(i)|}{2} \right\rceil

    .. math::

         \sum_{i \in \Gamma(j)} x_{i,j} = \left\lfloor \frac{|\Gamma(j)|}{2} \right\rfloor .

    Parameters
    ----------
    B : cnfgen.graphs.BipartiteGraph
        the graph vertices must have the 'bipartite' attribute
        set. Left vertices must have it set to 0 and the right ones to 1.
        A KeyException is raised otherwise.

    equalities : boolean
        use equations instead of inequalities to express the
        cardinality constraints.  (default: False)

    Returns
    -------
    A CNF object

    References
    ----------
    .. [1] Mladen Miksa and Jakob Nordstrom
           Long proofs of (seemingly) simple formulas
           Theory and Applications of Satisfiability Testing--SAT 2014 (2014)
    .. [2] Ivor Spence
           sgen1: A generator of small but difficult satisfiability benchmarks
           Journal of Experimental Algorithmics (2010)
    .. [3] Allen Van Gelder and Ivor Spence
           Zero-One Designs Produce Small Hard SAT Instances
           Theory and Applications of Satisfiability Testing--SAT 2010(2010)

    """
    B = BipartiteGraph.normalize(B)

    Left, Right = B.parts()

    description = "Subset cardinality formula for {0}".format(B.name)
    F = CNF(description=description)

    e = F.new_bipartite_edges(B, label='x_{{{0},{1}}}')

    for u in Left:

        hceil = (B.right_degree(u)+1) // 2
        if equalities:
            F.add_linear(e(u, None), '==', hceil)
        else:
            F.add_loose_majority(e(u, None))

    for v in Right:

        hfloor = B.left_degree(v) // 2
        if equalities:
            F.add_linear(e(None, v), '==', hfloor)
        else:
            F.add_loose_minority(e(None, v))

    return F
