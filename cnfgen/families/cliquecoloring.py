#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the clique-coloring formula
"""

from itertools import combinations
from cnfgen.formula.cnf import CNF
from cnfgen.localtypes import non_negative_int

def CliqueColoring(n, k, c, formula_class=CNF):
    r"""Clique-coloring CNF formula

    The formula claims that a graph :math:`G` with :math:`n` vertices
    simultaneously contains a clique of size :math:`k` and a coloring
    of size :math:`c`.

    If :math:`k = c + 1` then the formula is clearly unsatisfiable,
    and it is the only known example of a formula hard for cutting
    planes proof system. [1]_

    Variables :math:`e_{u,v}` to encode the edges of the graph.

    Variables :math:`q_{i,v}` encode a function from :math:`[k]` to
    :math:`[n]` that represents a clique.

    Variables :math:`r_{v,\ell}` encode a function from :math:`[n]` to
    :math:`[c]` that represents a coloring.

    Parameters
    ----------
    n : number of vertices in the graph
    k : size of the clique
    c : size of the coloring

    Returns
    -------
    A CNF object

    References
    ----------
    .. [1] Pavel Pudlak.
           Lower bounds for resolution and cutting plane proofs and
           monotone computations.
           Journal of Symbolic Logic (1997)

    """
    non_negative_int(n, 'n')
    non_negative_int(k, 'k')
    non_negative_int(c, 'c')

    description = "There is a graph of {0} vertices with a {1}-clique and a {2}-coloring".format(
        n, k, c)
    F = formula_class(description=description)

    # Variables
    e = F.new_combinations(n,2,label='e_{{{}}}')
    q = F.new_mapping(k,n,label='q_{{{0},{1}}}')
    r = F.new_mapping(n,c,label='r_{{{0},{1}}}')


    # some vertex is i'th member of clique
    F.force_complete_mapping(q)
    F.force_functional_mapping(q)
    F.force_injective_mapping(q)

    for u, v in e.indices():
        for i, j in combinations(q.domain(), 2):
            F.add_clause([e(u, v), -q(i, u), -q(j, v)])
            F.add_clause([e(u, v), -q(i, v), -q(j, u)])

    # every vertex v has exactly one colour
    F.force_complete_mapping(r)
    F.force_functional_mapping(r)

    # neighbours have distinct colours
    for u, v in e.indices():
        for ell in r.range():
            F.add_clause([-e(u, v), -r(u, ell), -r(v, ell)])
    return F
