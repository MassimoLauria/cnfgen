#!/usr/bin/env python

import random
from copy import copy

from cnfgen.formula.cnf import CNF


def Shuffle(F,
            polarity_flips='shuffle',
            variables_permutation='shuffle',
            clauses_permutation='shuffle'):
    """Reshuffle the given formula F

    Returns a formula logically equivalent to `F` with the
    following transformations applied the following order:

    1. Polarity flips,  specified as one of the following
       - string 'fixed': no flips is applied
       - string 'shuffle': each variable is subjected
         to a random flip of polarity
       - a list of `-1` and `+1` of length equal to
         the number of the variables in the formula `F`.

    2. Variable shuffling, specified as one of the following
       - string 'fixed': no shuffling
       - string 'shuffle': the variable order is randomly permuted
       - an sequence of integer which represents a permutation of [1,...,N],
         where N is the number of the variable in the formula. The i-th variable
         is mapped to the i-th index in the sequence.

    3. Clauses shuffling, specified as one of the following
       - string 'fixed': no shuffling
       - string 'shuffle': the clauses are randomly permuted
       - an sequence S of integer which represents a permutation of [0,...,M-1],
         where M is the number of the variable in the formula. The i-th clause in F
         is going to be at position S[i] in the new formula.

    Parameters
    ----------
    F : cnfgen.formula.cnf.CNF
        formula to be shuffled
    polarity_flips: string or iterable(int)
        Specifies the flips of polarity
    variables_permutation: string or iterable(int)
        Specifies the permutation of the variables.
    clauses_permutation: string or iterable(int)
        Specifies the permutation of the clauses.
    """

    # empty cnf
    out = CNF()
    out.header = copy(F.header)
    if 'description' in out.header:
        out.header['description'] += " (reshuffled)"

    i = 1
    while 'transformation {}'.format(i) in out.header:
        i += 1
    out.header['transformation {}'.format(i)] = "Formula reshuffling"

    N = F.number_of_variables()
    M = F.number_of_clauses()
    out.update_variable_number(N)

    # Manage the parameters
    perr = 'polarity_flips is either \'fixed\', \'shuffle\' or in {-1,+1]}^n'
    verr = 'variables_permutation is either \'fixed\', \'shuffle\' or a permutation of [1,...,N]'
    cerr = 'clauses_permutation is either \'fixed\', \'shuffle\' or a permutation of [0,...,M-1]'

    # polarity flips
    if polarity_flips == 'fixed':
        polarity_flips = [1] * N
    elif polarity_flips == 'shuffle':
        polarity_flips = [random.choice([-1, 1]) for x in range(N)]
    else:
        if len(polarity_flips) != N:
            raise ValueError(perr)
        for i in range(N):
            if abs(polarity_flips[i]) != 1:
                raise ValueError(perr)

    # variables permutation
    if variables_permutation == 'fixed':
        variables_permutation = range(1, N+1)
    elif variables_permutation == 'shuffle':
        variables_permutation = list(range(1, N+1))
        random.shuffle(variables_permutation)
    else:
        if len(variables_permutation) != N:
            raise ValueError(verr)
        tmp = sorted(variables_permutation)
        for i in range(N):
            if i+1 != tmp[i]:
                raise ValueError(verr)

    #
    # permutation of clauses
    #
    if clauses_permutation == 'fixed':
        clauses_mapping = ((i, i) for i in range(M))
    elif clauses_permutation == 'shuffle':
        tmp = list(range(M))
        random.shuffle(tmp)
        clauses_mapping = sorted(enumerate(tmp), key=lambda x: x[1])
    else:
        if len(clauses_permutation) != M:
            raise ValueError(cerr)
        tmp = sorted(clauses_permutation)
        for i in range(M):
            if i != tmp[i]:
                raise ValueError(cerr)
        clauses_mapping = sorted(enumerate(clauses_permutation), key=lambda x: x[1])


    # precompute literal mapping
    substitution = [None] * (2 * N + 1)
    for i in range(1, N+1):
        substitution[i] = polarity_flips[i-1] * variables_permutation[i-1]
        substitution[-i] = -substitution[i]

    # load clauses
    for (old, new) in clauses_mapping:
        assert new == out.number_of_clauses()
        out.add_clause(substitution[lit] for lit in F[old])

    return out
