import io

from cnfgen import CNF
from cnfgen import RandomKCNF
from cnfgen import Shuffle
from cnfgen import FlipPolarity
from cnfgen import cnfgen

from tests.utils import assertCnfEqual, redirect_stdin, redirect_stdout


def test_double_flip():
    for _ in range(10):
        cnf = RandomKCNF(4, 10, 100)
        ddcnf = FlipPolarity(FlipPolarity(cnf))
        assertCnfEqual(cnf, ddcnf)


def test_simple_flip():
    flipped = FlipPolarity(CNF([[-1, -2, +3]]))
    print(flipped.number_of_variables())
    print(flipped.number_of_clauses())
    expected = CNF([[+1, +2, -3]])
    assertCnfEqual(expected, flipped)

def test_polarity_shuffle_vs_flip():
    cnf = CNF([[+1, +2, -3]])

    variable_permutation = cnf.variables()
    clause_permutation = range(len(cnf))
    polarity_flip = [-1] * cnf.number_of_variables()

    shuffled = Shuffle(cnf, polarity_flip,
                       variable_permutation,
                       clause_permutation)
    flipped = FlipPolarity(cnf)
    assertCnfEqual(flipped, shuffled)


def test_cmdline_flip():

    source = RandomKCNF(4, 10, 3)
    expected = FlipPolarity(source)

    input_stream = io.StringIO(source.to_dimacs())

    with redirect_stdin(input_stream):
        cli = cnfgen(
            ['cnfgen', '-q', 'dimacs', '-', '-T', 'flip'],
            mode='string')

    lib = expected.to_dimacs()
    assert lib == cli
