from cnfgen import CNF, RandomKCNF, PigeonholePrinciple
from cnfgen import Shuffle
from cnfgen.clitools import cnfgen

import random
from tests.utils import assertCnfEqual


def test_identity():
    cnf = RandomKCNF(4, 10, 100)

    variable_permutation = list(cnf.variables())
    clause_permutation = list(range(100))
    polarity_flip = [1] * 10

    shuffle = Shuffle(cnf, variable_permutation, clause_permutation,
                      polarity_flip)
    assertCnfEqual(cnf, shuffle)


def test_variable_permutation():
    cnf = CNF([[(True, 'x'), (True, 'y'), (False, 'z')]])
    variable_permutation = ['y', 'z', 'x']
    clause_permutation = list(range(1))
    polarity_flip = [1] * 3
    shuffle = Shuffle(cnf, variable_permutation, clause_permutation,
                      polarity_flip)
    assert list(shuffle.variables()) == variable_permutation
    assert list(shuffle.clauses()) == list(cnf.clauses())


def test_polarity_flip():
    cnf = CNF([[(True, 'x'), (True, 'y'), (False, 'z')]])
    variable_permutation = list(cnf.variables())
    clause_permutation = list(range(1))
    polarity_flip = [1, -1, -1]
    shuffle = Shuffle(cnf, variable_permutation, clause_permutation,
                      polarity_flip)
    expected = CNF([[(True, 'x'), (False, 'y'), (True, 'z')]])
    assertCnfEqual(expected, shuffle)


def test_variable_and_polarity_flip():
    cnf = CNF([[(True, 'x'), (True, 'y'), (False, 'z')]])
    variable_permutation = ['y', 'z', 'x']
    clause_permutation = list(range(1))
    polarity_flip = [1, -1, -1]
    shuffle = Shuffle(cnf, variable_permutation, clause_permutation,
                      polarity_flip)
    expected = CNF([[(False, 'y'), (True, 'z'), (True, 'x')]])
    assertCnfEqual(expected, shuffle)


def test_inverse():
    cnf = RandomKCNF(4, 10, 100)

    # Generate random variable, clause and polarity permutations.
    # but keep the indices for the variables, since they are strings.
    indexed_and_shuffled_vars = list(enumerate(cnf.variables()))
    random.shuffle(indexed_and_shuffled_vars)

    variables_permutation = [v for i, v in indexed_and_shuffled_vars]

    clauses_permutation = list(range(100))
    random.shuffle(clauses_permutation)

    polarity_flips = [random.choice([-1, 1]) for x in range(10)]

    # First shuffle
    shuffle1 = Shuffle(cnf, variables_permutation, clauses_permutation,
                       polarity_flips)

    # The inverse variables permutation is the original list of vars
    i_variables_permutations = list(cnf.variables())

    # The inverse clause permutation is the group inverse permutation.
    i_clauses_permutation = [0] * len(clauses_permutation)
    for nidx, oidx in enumerate(clauses_permutation):
        i_clauses_permutation[oidx] = nidx

    # The polarity flips are applied before variables permutation.
    # So if we flipped the i-th variable before, now we want to flip the
    # sigma(i)-th variable.
    i_polarity_flips = [
        polarity_flips[i] for i, v in indexed_and_shuffled_vars
    ]

    # Inverse shuffle.
    shuffle2 = Shuffle(shuffle1, i_variables_permutations,
                       i_clauses_permutation, i_polarity_flips)
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
    lib = Fs.dimacs(export_header=False)
    random.seed(167)
    cli = cnfgen(["cnfgen", "-q", "php", 7, 6, '-T', "shuffle"], mode='string')
    assert lib == cli
