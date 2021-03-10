import random
import io
import pytest

from itertools import product

from cnfgen.clitools import cnfshuffle
from cnfgen import Shuffle, RandomKCNF

from tests.utils import redirect_stdin, redirect_stdout

def run(cnf, seed, p='shuffle', v='shuffle', c='shuffle'):
    random.seed('45')
    shuffle = Shuffle(cnf,
                      polarity_flips=p,
                      variables_permutation=v,
                      clauses_permutation=c)
    lib = shuffle.to_dimacs()

    parameters = ['cnfshuffle', '-q', '--input', '-', '--seed', '45']
    if p == 'fixed':
        parameters.append('-p')
    if v == 'fixed':
        parameters.append('-v')
    if c == 'fixed':
        parameters.append('-c')

    print(cnf.to_dimacs())
    input = io.StringIO(cnf.to_dimacs())
    with redirect_stdin(input):
        cli = cnfshuffle(parameters, mode='string')
    return lib, cli

def test_cmdline_cnfshuffle():
    cnf = RandomKCNF(4, 10, 3)
    cli,lib = run(cnf, 45)
    assert cli,lib

paramcases = product([23,45,10,24532],
                ['fixed','shuffle'],
                ['fixed','shuffle'],
                ['fixed','shuffle'])

@pytest.mark.parametrize("seed,p,v,c", paramcases)
def test_cmdline_cnfshuffle_p(seed,p,v,c):
    cnf = RandomKCNF(4, 10, 3)
    lib, cli = run(cnf, seed, p,v,c)
    assert lib, cli
