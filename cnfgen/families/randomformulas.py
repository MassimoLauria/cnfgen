#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Random CNF Formulas
"""

import itertools
import random

from cnfgen.formula.cnf import CNF
from cnfgen.localtypes import non_negative_int

def clause_satisfied(cls, assignments):
    """Test whether a clause is satisfied by all assignments

Test if clauses `cls` is satisfied by all assigment in the
list assignments.
"""
    for assignment in assignments:
        for lit in cls:
            if lit in assignment:
                break
        else:
            return False
    return True


def sample_clauses(k, n, m, planted_assignments):
    """Sample m random k-clauses on a set of n variables

First it tries sparse sampling:
- samples with repetition which is fast
- filters bad samples

If after enough samples we haven't got enough clauses we use dense
sampling, namely we generare all possible clauses and pick at random
m of them. This approach always succeeds, but is quite slower and
wasteful for just few samples."""
    sampled = set()
    variables = range(1,n+1)
    t = 0
    clauses = []
    while len(clauses) < m and t < 10 * m:
        t += 1

        selection = sorted(random.sample(variables, k))
        cls = [v*random.choice([1, -1]) for v in selection]
        tcls = tuple(cls)

        if tcls in sampled:
            continue

        if not clause_satisfied(cls, planted_assignments):
            continue

        sampled.add(tcls)
        clauses.append(cls)

    if len(clauses) == m:
        return clauses

    # dense sampling
    fullset = list(all_clauses(k, n, planted_assignments))
    if len(fullset) < m:
        if len(planted_assignments)>0:
            raise ValueError("Not enough clauses satisfying the planted assignment")
        else:
            raise ValueError("Too many clauses requested")
    return random.sample(fullset, m)


def all_clauses(k, n, planted_assignments):
    for domain in itertools.combinations(range(1, n+1), k):
        for polarity in itertools.product([-1, 1], repeat=k):

            cls = [p*v for p,v in zip(polarity,domain)]
            if clause_satisfied(cls, planted_assignments):
                yield cls




def RandomKCNF(k, n, m, seed=None, planted_assignments=None, formula_class=CNF):
    """Build a random k-CNF

    Sample :math:`m` clauses over :math:`n` variables, each of width
    :math:`k`, uniformly at random. The sampling is done without
    repetition, meaning that whenever a randomly picked clause is
    already in the CNF, it is sampled again.

    Parameters
    ----------
    k : int
       width of each clause

    n : int
       number of variables to choose from. The resulting CNF object
       will contain n variables even if some are not mentioned in the clauses.

    m : int
       number of clauses to generate

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

    descr = "Random {}-CNF over {} variables and {} clauses".format(k, n, m)
    F = formula_class(description=descr)

    F.update_variable_number(n)
    try:
        for clause in sample_clauses(k, n, m, planted_assignments):
            F.add_clause(clause, check=False)
    except ValueError:
        raise ValueError(
            "The number of clauses available is less than m")

    return F
