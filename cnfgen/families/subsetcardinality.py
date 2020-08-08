#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of subset cardinality formulas
"""

from cnfgen.cnf import CNF

from cnfgen.graphs import bipartite_sets, enumerate_edges, neighbors


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
    B : networkx.Graph
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
    Left, Right = bipartite_sets(B)

    description = "Subset cardinality formula for {0}".format(B.name)
    ssc = CNF(description=description)

    def var_name(u, v):
        """Compute the variable names."""
        if u <= v:
            return 'x_{{{0},{1}}}'.format(u, v)
        else:
            return 'x_{{{0},{1}}}'.format(v, u)

    for u in Left:
        for v in neighbors(B, u):
            ssc.add_variable(var_name(u, v))

    for u in Left:
        edge_vars = [var_name(u, v) for v in neighbors(B, u)]

        if equalities:
            for cls in CNF.exactly_half_ceil(edge_vars):
                ssc.add_clause(cls, strict=True)
        else:
            for cls in CNF.loose_majority_constraint(edge_vars):
                ssc.add_clause(cls, strict=True)

    for v in Right:
        edge_vars = [var_name(u, v) for u in neighbors(B, v)]

        if equalities:
            for cls in CNF.exactly_half_floor(edge_vars):
                ssc.add_clause(cls, strict=True)
        else:
            for cls in CNF.loose_minority_constraint(edge_vars):
                ssc.add_clause(cls, strict=True)

    return ssc
