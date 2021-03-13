#!/usr/bin/env python
# -*- coding:utf-8 -*-

from itertools import combinations
from itertools import product

import networkx

from cnfgen.formula.cnf import CNF
from cnfgen.families.tseitin import TseitinFormula
from cnfgen.localtypes import positive_int
from cnfgen.graphs import Graph


def PitfallFormula(v, d, ny, nz, k):
    """Pitfall Formula

    The Pitfall formula was designed to be specifically easy for
    Resolution and hard for common CDCL heuristics. The formula is
    unsatisfiable and consists of three parts: an easy formula, a hard
    formula, and a pitfall misleading the solver into working with the
    hard part.

    The hard part are several copies of an unsatisfiable Tseitin
    formula on a random regular graph. The pitfall part is made up of
    a few gadgets over (primarily) two sets of variables: pitfall
    variables, which point the solver towards the hard part after
    being assigned, and safety variables, which prevent the gadget
    from breaking even if a few other variables are assigned.

    For more details, see the corresponding paper [1]_.

    Parameters
    ----------
    v : positive integer
        number of vertices of the Tseitin graph
    d : positive integer
        degree of the Tseitin graph
    ny : positive integer
         number of pitfall variables
    nz : positive integer
         number of safety variables
    k : positive, even integer
        number of copies of the hard and pitfall parts; controls how
        easy the easy part is

    Returns
    -------
    A CNF object

    Raises
    ------
    ValueError
        When `v < d` or `d*v` is odd there is no d-regular graph on `v` verices.

    References
    ----------
    .. [1] Marc Vinyals.
           Hard examples for common variable decision heuristics.
           In, AAAI 2020 (pp. 1652–1659).
    """
    positive_int(v, 'v')
    positive_int(d, 'd')
    positive_int(ny, 'ny')
    positive_int(nz, 'nz')
    positive_int(k, 'k')
    if k % 2 != 0:
        raise ValueError("argument 'k' must be even.")

    if (d > v) or (v * d % 2 == 1):
        raise ValueError(
            "No regular {}-degree graph with {}-vertices exists.\n".format(
                d, v) +
            "It requires  degree <= #vertices and degree*#vertices even")
    phi = CNF(
        description=
        'Pitfall Formula with parameters (v={},d={},ny={},nz={},k={})'.format(
            v, d, ny, nz, k))

    graph = networkx.random_regular_graph(d, v)
    graph = Graph.normalize(graph)

    # Template for the hard variables
    T = TseitinFormula(graph, [True])
    nx = T.number_of_variables()

    # Hard variables (we waste position 0 to start indexing from 1)
    # now X[j](u,v) is the edge variable for {u,v} in the j-th copy.
    X = [None]
    for j in range(1, k + 1):
        jlabel = 'e[{}]'.format(j) + '_{{{},{}}}'
        X.append(phi.new_graph_edges(graph, label=jlabel))

    # Easy variables
    Y = phi.new_block(k, ny, label='y_{{{},{}}}')

    # Pipe and Pitfall variables
    Z = phi.new_block(k, nz, label='z_{{{},{}}}')
    P = phi.new_block(k, nx + nz, label='p_{{{},{}}}')
    # Tail variables
    A = phi.new_block(k, 3, label='a_{{{},{}}}')

    def shift_edgelit(j, lit):
        sign = lit // abs(lit)
        return sign * X[j][0] + lit - 1

    # Hard part
    # Copy the Tseitin formula for k times
    # with a prefix of Z(j,..)
    for j in range(1, k + 1):
        append = list(Z(j, None))
        for clause in T:
            shifted = [shift_edgelit(j, lit) for lit in clause]
            phi.add_clause(shifted + append)

    # Pitfall gadgets
    # any two easy variables trigger the p's
    for j in range(1, k + 1):
        for (y1, y2) in combinations(Y(j, None), 2):
            for p in P(j, None):
                phi.add_clause([y1, y2, -p])

    # Pipe gadgets
    def pipe(y, PP, XX, ZZ):
        PP = list(PP)
        XX = list(XX)
        ZZ = list(ZZ)
        S = XX + ZZ
        CY = [y]
        C = []
        for (s, PPP) in zip(S, combinations(PP, len(PP) - 1)):
            CP = list(PPP)
            CS = C
            if len(CS) + 1 == len(S):
                # C_{m+n} does not contain z_1
                del CS[nx]
            phi.add_clause(CY + CP + CS + [-s])
            C.append(s)

    for j in range(1, k + 1):
        for y in Y(j, None):
            pipe(y, P(j, None), X[j], Z(j, None))

    # Tail gadgets
    for j in range(1, k + 1):
        for (y, z) in product(Y(j, None), Z(j, None)):
            phi.add_clause([-A(j, 1), A(j, 3), -z])
            phi.add_clause([-A(j, 2), -A(j, 3), -z])
            phi.add_clause([A(j, 1), -z, -y])
            phi.add_clause([A(j, 2), -z, -y])

    ### Easy part
    # Gamma
    for i in range(1, ny, 2):
        clause = []
        for j in range(1, k + 1):
            clause.extend([-Y(j, i), -Y(j, i + 1)])
        phi.add_clause(clause)

    return phi
