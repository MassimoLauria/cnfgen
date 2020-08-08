#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfgen.cnf import CNF

import cnfgen.families

from itertools import product

import networkx
from cnfgen.families.tseitin import TseitinFormula
from itertools import combinations


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
    if v <= 0:
        raise ValueError("v must be positive.")
    if d <= 0:
        raise ValueError("d must be positive.")
    if ny <= 0:
        raise ValueError("ny must be positive.")
    if nz <= 0:
        raise ValueError("nz must be positive.")
    if k <= 0:
        raise ValueError("k must be positive.")
    if k % 2 != 0:
        raise ValueError("k must be even.")

    def xname(j, x):
        return "{}_{}".format(x, j)

    phi = CNF(
        description=
        'Pitfall Formula with parameters (v={},d={},ny={},nz={},k={})'.format(
            v, d, ny, nz, k))
    try:
        graph = networkx.random_regular_graph(d, v)
    except networkx.exception.NetworkXError:
        raise ValueError("""No regular {}-degree graph with {}-vertices exists.
Degree d must less than the number v of vertices,
and d*v must be even.""".format(d, v))

    charge = [1] + [0] * (v - 1)
    ts = TseitinFormula(graph, charge)

    X_ = list(ts.variables())
    nx = len(X_)

    ### Variables
    X = [0] * k
    P = [0] * k
    Y = [0] * k
    Z = [0] * k
    A = [0] * k
    for j in range(k):
        X[j] = [xname(j, x) for x in X_]
        P[j] = ["p_{}_{}".format(j, i) for i in range(nx + nz)]
        Y[j] = ["y_{}_{}".format(j, i) for i in range(ny)]
        Z[j] = ["z_{}_{}".format(j, i) for i in range(nz)]
        A[j] = ["a_{}_{}".format(j, i) for i in range(3)]

    for YY in Y:
        for y in YY:
            phi.add_variable(y)

    for XX in X:
        for x in XX:
            phi.add_variable(x)

    ### Hard part
    # Ts_j
    for j in range(k):
        append = [(True, z) for z in Z[j]]
        for C in ts:
            CC = [(p, xname(j, x)) for (p, x) in C]
            phi.add_clause(CC + append)

    ### Pitfall part
    # Psi
    def pitfall(y1, y2, PP):
        CY = [(True, y1), (True, y2)]
        for p in PP:
            phi.add_clause(CY + [(False, p)])

    for j in range(k):
        for (y1, y2) in combinations(Y[j], 2):
            pitfall(y1, y2, P[j])

    # Pi
    def pipe(y, PP, XX, ZZ):
        S = XX + ZZ
        CY = [(True, y)]
        C = []
        for (s, PPP) in zip(S, combinations(PP, len(PP) - 1)):
            CP = [(True, p) for p in PPP]
            CS = C
            if len(CS) + 1 == len(S):
                # C_{m+n} does not contain z_1
                del CS[nx]
            phi.add_clause(CY + CP + CS + [(False, s)])
            C.append((True, s))

    for j in range(k):
        for y in Y[j]:
            pipe(y, P[j], X[j], Z[j])

    # Delta
    def tail(y, z, AA):
        phi.add_clause([(False, AA[0]), (True, AA[2]), (False, z)])
        phi.add_clause([(False, AA[1]), (False, AA[2]), (False, z)])
        phi.add_clause([(True, AA[0]), (False, z), (False, y)])
        phi.add_clause([(True, AA[1]), (False, z), (False, y)])

    for j in range(k):
        for (y, z) in product(Y[j], Z[j]):
            tail(y, z, A[j])

    ### Easy part
    # Gamma
    split_gamma = 2
    for i in range(0, ny, split_gamma):
        phi.add_clause([(False, Y[j][i + ii]) for j in range(k)
                        for ii in range(split_gamma)])

    return phi
