from cnfgen import CNF, RandomKCNF, PigeonholePrinciple
from cnfgen import Shuffle
from cnfgen.clitools import cnfgen

import random
from tests.utils import assertCnfEqual


def test_identity():
    cnf = RandomKCNF(4, 10, 100)
    polarity_flips = [1] * 10
    variables_permutation = range(1,cnf.number_of_variables()+1)
    clauses_permutation = list(range(100))

    shuffle = Shuffle(cnf, polarity_flips,
                      variables_permutation, clauses_permutation)
    assertCnfEqual(cnf, shuffle)


def test_variable_permutation():
    cnf = CNF([[1, 2, -3]])
    polarity_flips = [1] * 3
    variables_permutation = [3, 1, 2]
    clauses_permutation = [0]
    shuffle = Shuffle(cnf,
                      polarity_flips,
                      variables_permutation,
                      clauses_permutation)
    expected = CNF([[3, 1, -2]])
    assertCnfEqual(expected, shuffle)


def test_polarity_flip():
    cnf = CNF([[1, 2, -3]])
    polarity_flips = [1, -1, -1]
    variables_permutation = [1, 2, 3]
    clauses_permutation = [0]
    shuffle = Shuffle(cnf,
                      polarity_flips,
                      variables_permutation,
                      clauses_permutation)
    expected = CNF([[1, -2, 3]])
    assertCnfEqual(expected, shuffle)


def test_variable_and_polarity_flip():
    cnf = CNF([[1, 2, -3]])
    polarity_flips = [1, -1, -1]
    variables_permutation = [3, 1, 2]
    clauses_permutation = [0]
    shuffle = Shuffle(cnf,
                      polarity_flips,
                      variables_permutation,
                      clauses_permutation)
    expected = CNF([[3, -1, 2]])
    assertCnfEqual(expected, shuffle)


def test_inverse():
    K = 4
    N = 10
    M = 100
    cnf = RandomKCNF(K, N, M)
    polarity_flips = [random.choice([-1, 1]) for x in range(N)]

    variables_permutation = list(range(1, N+1))
    random.shuffle(variables_permutation)

    clauses_permutation = list(range(M))
    random.shuffle(clauses_permutation)


    # First shuffle
    shuffle1 = Shuffle(cnf,
                       polarity_flips,
                       variables_permutation,
                       clauses_permutation)

    # Compute the inverse variables permutation
    i_variables_permutation = [0] * len(variables_permutation)
    for nidx, oidx in enumerate(variables_permutation, start=1):
        i_variables_permutation[oidx-1] = nidx

    # Compute the inverse clause permutation
    i_clauses_permutation = [0] * len(clauses_permutation)
    for nidx, oidx in enumerate(clauses_permutation):
        i_clauses_permutation[oidx] = nidx

    # The polarity flips are applied before variables permutation.
    # So if we flipped the i-th variable before, now we want to flip the
    # sigma(i)-th variable.
    i_polarity_flips = []
    for v in i_variables_permutation:
        i_polarity_flips.append(polarity_flips[v - 1])

    # Inverse shuffle.
    shuffle2 = Shuffle(shuffle1, i_polarity_flips, i_variables_permutation,
                       i_clauses_permutation)
    assertCnfEqual(shuffle2, cnf)


def test_deterministic():
    cnf = RandomKCNF(4, 10, 100)
    random.seed(42)
    shuffle = Shuffle(cnf)
    random.seed(42)
    shuffle2 = Shuffle(cnf)
    assertCnfEqual(shuffle2, shuffle)


def test_cli_vs_lib():
    F = PigeonholePrinciple(7, 6)
    random.seed(167)
    Fs = Shuffle(F)
    lib = Fs.to_dimacs()
    random.seed(167)
    cli = cnfgen(["cnfgen", "-q", "php", 7, 6, '-T', "shuffle"], mode='string')
    assert lib == cli
