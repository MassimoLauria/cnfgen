#!/usr/bin/env python

import random
from copy import copy

from cnfgen.cnf import CNF


def Shuffle(cnf,
            variables_permutation=None,
            clauses_permutation=None,
            polarity_flips=None):
    """ Reshuffle the given cnf. Returns a formula logically
    equivalent to the input with the following transformations
    applied in order:

    1. Polarity flips. polarity_flip is a {-1,1}^n vector. If the i-th
    entry is -1, all the literals with the i-th variable change its
    sign.

    2. Variable permutations. variable_permutation is a permutation of
    [vars(cnf)]. All the literals with the old i-th variable are
    replaced with the new i-th variable.

    3. Clause permutations. clause_permutation is a permutation of
    [0..m-1]. The resulting clauses are reordered according to the
    permutation.
"""

    # empty cnf
    out = CNF()
    out.header = copy(cnf.header)

    if 'description' in out.header:
        out.header['description'] += " (reshuffled)"

    i = 1
    while 'transformation {}'.format(i) in out.header:
        i += 1
    out.header['transformation {}'.format(i)] = "Formula reshuffling"

    variables = list(cnf.variables())
    N = len(variables)
    M = len(cnf)

    # variable permutation
    if variables_permutation is None:
        variables_permutation = variables
        random.shuffle(variables_permutation)
    else:
        assert len(variables_permutation) == N

    # polarity flip
    if polarity_flips is None:
        polarity_flips = [random.choice([-1, 1]) for x in range(N)]
    else:
        assert len(polarity_flips) == N

    #
    # substitution of variables
    #
    for v in variables_permutation:
        out.add_variable(v)

    substitution = [None] * (2 * N + 1)
    reverse_idx = dict([(v, i) for (i, v) in enumerate(out.variables(), 1)])
    polarity_flips = [None] + polarity_flips

    for i, v in enumerate(cnf.variables(), 1):
        substitution[i] = polarity_flips[i] * reverse_idx[v]
        substitution[-i] = -substitution[i]

    #
    # permutation of clauses
    #
    if clauses_permutation is None:
        clauses_permutation = list(range(M))
        random.shuffle(clauses_permutation)

    # load clauses
    out._clauses = [None] * M
    for (old, new) in enumerate(clauses_permutation):
        out._clauses[new] = tuple(substitution[lit]
                                  for lit in cnf._clauses[old])

    return out
