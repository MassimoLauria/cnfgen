#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfformula.cnf import CNF

import cnfformula.families

from itertools import product

import networkx
from cnfformula.families.tseitin import TseitinFormula
from itertools import combinations


def PitfallFormula(v, d, ny, nz, k):
    """Pitfall Formula

    The Pitfall formula has been designed by Marc Vinyals [1]_ to be
    specifically easy for Resolution and hard for common CDCL
    heuristics. The formula is unsatisfiable and is the union of an
    easy to refute and several copies of unsatisfiable Tseitin
    formulas on random regular graphs. For more details on this
    formula I suggest to read the corresponding paper.

    Parameters
    ----------
    v : positive integer
        number of vertices in the Tseitin formulas
    d : positive integer
        graph degree in the Tseitin formulas  
    ny : positive integer
    nz : positive integer
    k : positive integer

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

    def xname(j, x):
        return "{}_{}".format(x, j)

    phi = CNF()
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

    # Ts_j
    for j in range(k):
        append = [(True, z) for z in Z[j]]
        for C in ts:
            CC = [(p, xname(j, x)) for (p, x) in C]
            phi.add_clause(CC + append)

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

    # Gamma
    split_gamma = 2
    for i in range(0, ny, split_gamma):
        phi.add_clause([(False, Y[j][i + ii]) for j in range(k)
                        for ii in range(split_gamma)])

    return phi
