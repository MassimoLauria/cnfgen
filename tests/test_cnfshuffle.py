import random
import io
import pytest

from cnfgen.clitools import cnfshuffle
from cnfgen import Shuffle, RandomKCNF

from tests.shufflereference import stableshuffle
from tests.utils import redirect_stdin, redirect_stdout


def test_backwards_compatible():
    cnf = RandomKCNF(4, 10, 100)
    random.seed(44)

    lib = Shuffle(cnf).dimacs(export_header=False)

    input = io.StringIO(cnf.dimacs())
    output = io.StringIO()
    random.seed(44)
    with redirect_stdin(input), redirect_stdout(output):
        stableshuffle(input, output)
        assert lib + '\n' == output.getvalue()


def test_cmdline_reshuffler():
    cnf = RandomKCNF(4, 10, 3)
    random.seed('45')
    shuffle = Shuffle(cnf)
    lib = shuffle.dimacs(export_header=False)

    input = io.StringIO(cnf.dimacs())
    parameters = ['cnfshuffle', '-q', '--input', '-', '--seed', '45']
    with redirect_stdin(input):
        cli = cnfshuffle(parameters, mode='string')
    assert lib == cli


def equivalence_check_helper(cnf, dimacs_permutation, clause_permutation,
                             polarity_flip):
    """Test if library and reference implementations give the same shuffle.

    dimacs_permutation must be a permutation of [1..n] 
    """
    variables = list(cnf.variables())
    massimos_fancy_input = [variables[p - 1] for p in dimacs_permutation]

    random.seed(43)
    shuffle = Shuffle(cnf, massimos_fancy_input, clause_permutation,
                      polarity_flip)
    lib = shuffle.dimacs(export_header=False) + "\n"

    input = io.StringIO(cnf.dimacs(export_header=False))
    output = io.StringIO()
    random.seed(43)
    with redirect_stdin(input), redirect_stdout(output):
        stableshuffle(input, output, dimacs_permutation, clause_permutation,
                      polarity_flip)
    assert lib == output.getvalue()


def test_identity_equivalence():
    cnf = RandomKCNF(2, 3, 2)
    dimacs_permutation = [1, 2, 3]
    clause_permutation = [0, 1]
    polarity_flip = [1] * 3
    equivalence_check_helper(cnf, dimacs_permutation, clause_permutation,
                             polarity_flip)


def test_random_equivalence_small():
    cnf = RandomKCNF(4, 10, 10)
    dimacs_permutation = list(range(1, 11))
    random.shuffle(dimacs_permutation)
    clause_permutation = list(range(10))
    random.shuffle(clause_permutation)
    polarity_flip = [random.choice([-1, 1]) for x in range(10)]
    equivalence_check_helper(cnf, dimacs_permutation, clause_permutation,
                             polarity_flip)


def test_random_equivalence():
    cnf = RandomKCNF(4, 10, 100)
    dimacs_permutation = list(range(1, 11))
    random.shuffle(dimacs_permutation)
    clause_permutation = list(range(100))
    random.shuffle(clause_permutation)
    polarity_flip = [random.choice([-1, 1]) for x in range(10)]
    equivalence_check_helper(cnf, dimacs_permutation, clause_permutation,
                             polarity_flip)
