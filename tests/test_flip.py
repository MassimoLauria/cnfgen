import io

from cnfformula import CNF
from cnfformula import RandomKCNF
from cnfformula import Shuffle
from cnfformula import FlipPolarity

from cnfgen import cnftransform
from tests.utils import assertCnfEqual, redirect_stdin, redirect_stdout


def test_double_flip():
    for _ in range(10):
        cnf = RandomKCNF(4, 10, 100)
        ddcnf = FlipPolarity(FlipPolarity(cnf))
        assertCnfEqual(cnf, ddcnf)


def test_simple_flip():
    flipped = FlipPolarity(CNF([[(False, 'x'), (False, 'y'), (True, 'z')]]))
    expected = CNF([[(True, 'x'), (True, 'y'), (False, 'z')]])
    assertCnfEqual(expected, flipped)


def test_polarity_shuffle_vs_flip():
    cnf = CNF([[(True, 'x'), (True, 'y'), (False, 'z')]])

    variable_permutation = list(cnf.variables())
    clause_permutation = list(range(len(cnf)))
    polarity_flip = [-1] * len(variable_permutation)

    shuffled = Shuffle(cnf, variable_permutation, clause_permutation,
                       polarity_flip)
    flipped = FlipPolarity(cnf)
    assertCnfEqual(flipped, shuffled)


def test_cmdline_flip():

    source = RandomKCNF(4, 10, 3)
    expected = FlipPolarity(source)

    input_stream = io.StringIO(source.dimacs())

    with redirect_stdin(input_stream):
        cli = cnftransform(
            ['cnftransform', '-q', '--input', '-', '--output', '-', 'flip'],
            mode='string')

    lib = expected.dimacs(export_header=False)
    assert lib == cli
