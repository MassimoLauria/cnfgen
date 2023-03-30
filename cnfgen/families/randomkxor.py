#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Random CNF Formulas
"""

import itertools
import random

from cnfgen.formula.cnf import CNF
from cnfgen.localtypes import non_negative_int

def parity_satisfied(X, b, assignments):
    """Test whether a clause is satisfied by all assignments

Test if clauses `cls` is satisfied by all assigment in the
list assignments.
"""
    for assignment in assignments:
        value=0
        for xi in X:
            if xi in assignment:
                value += 1
            elif -xi in assignment:
                value += 0
            else:
                raise ValueError("Xor value undefined for some planted assignment")
        if value % 2 !=b:
            return False
    return True


def sample_parities(k, n, m, planted_assignments):
    """Sample m random k-parities on a set of n variables

First it tries sparse sampling:
- samples with repetition which is fast
- filters bad samples

If after enough samples we haven't got enough parities we use dense
sampling, namely we generare all possible parities and pick at random
m of them. This approach always succeeds, but is quite slower and
wasteful for just few samples."""
    # Sparse sampling
    sampled_set = set()
    sampled_list = []
    variables = range(1,n+1)
    t = 0
    while len(sampled_list) < m and t < 10 * m:
        t += 1

        X = sorted(random.sample(variables, k))
        b      = random.randint(0,1)
        sample = tuple(X+[b])

        # already sampled?
        if sample in sampled_set:
            continue
        # satisfies the planted assignments?
        if not parity_satisfied(X,b,planted_assignments):
            continue

        sampled_set.add(sample)
        sampled_list.append((X,b))
    # sparse sampling was good
    if len(sampled_list) >= m:
        return sampled_list

    # Dense sampling
    fullset = list(all_good_parities(k,n,planted_assignments))
    if len(fullset) < m:
        if len(planted_assignments)>0:
            raise ValueError("Not enough parities satisfying the planted assignment")
        else:
            raise ValueError("Too many parities requested")
    return random.sample(fullset, m)


def all_good_parities(k, n, planted_assignments):
    for X in itertools.combinations(range(1, n+1), k):
        if parity_satisfied(X,0,planted_assignments):
            yield X,0
        if parity_satisfied(X,1,planted_assignments):
            yield X,1




def RandomKXOR(k, n, m, seed=None, planted_assignments=None, formula_class=CNF):
    """Build a random k-XOR

    Sample :math:`m` parity constraints over :math:`n` variables, each of width
    :math:`k`, uniformly at random. The sampling is done without
    repetition, meaning that whenever a randomly picked parity is
    is already in the formula, it is sampled again.

    Parameters
    ----------
    k : int
       width of each parity

    n : int
       number of variables to choose from. The resulting CNF object
       will contain n variables even if some are not mentioned in the clauses.

    m : int
       number of parity constraints to generate

    seed : hashable object
       seed of the random generator

    planted_assignments : iterable(lists), optional
       a set of total/partial assigments such that all clauses in the formula
       will be satisfied by all of them. Each partial assignment is a sequence of literals.
       Undefined behaviour if some assignment contains opposite literals.

    Returns
    -------
    a CNF object

    Raises
    ------
    ValueError
        when some paramenter is negative, or when k>n.

    """
    non_negative_int(n, 'n')
    non_negative_int(m, 'm')
    non_negative_int(k, 'k')

    if seed is not None:
        random.seed(seed)

    if planted_assignments is None:
        planted_assignments = []

    if k > n:
        raise ValueError("clauses width is {}, and we only have {} variables".format(k,n))

    descr = "Random {}-xor over {} variables and {} clauses".format(k, n, m)
    F = formula_class(description=descr)

    F.update_variable_number(n)
    try:
        for X,b in sample_parities(k, n, m, planted_assignments):
            F.add_parity(X,b, check=False)
    except ValueError:
        raise ValueError(
            "The number of XORs available is less than m")

    return F
