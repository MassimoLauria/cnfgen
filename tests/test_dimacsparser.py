from cnfformula import CNF
from cnfformula import RandomKCNF
from cnfformula import readCNF

import io
import pytest

from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables
from cnfgen import cnfgen
from cnfgen.cmdline import redirect_stdin, CLIError


def test_empty_file():
    dimacs = io.StringIO()
    with pytest.raises(ValueError):
        readCNF(dimacs)


def test_empty_cnf():
    dimacs = io.StringIO("p cnf 0 0\n")
    cnf = readCNF(dimacs)
    assertCnfEqual(cnf, CNF())


def test_comment_only_file():
    dimacs = io.StringIO("c Hej!\n")
    with pytest.raises(ValueError):
        readCNF(dimacs)


def test_invalid_file():
    dimacs = io.StringIO("Hej!\n")
    with pytest.raises(ValueError):
        readCNF(dimacs)


def test_commented_empty_cnf():
    dimacs = io.StringIO("c Hej!\np cnf 0 0\n")
    cnf = readCNF(dimacs)
    assertCnfEqual(cnf, CNF())


def test_one_clause_cnf():
    dimacs = io.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
    cnf = readCNF(dimacs)
    assertCnfEqual(cnf, CNF([[(True, 1), (False, 2)]]))


def test_one_var_cnf():
    dimacs = io.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
    cnf = readCNF(dimacs)
    assertCnfEqual(cnf, CNF([[(True, 1)], [(False, 1)]]))


def test_double_conversion():
    cnf = CNF()
    cnf.add_variable(1)
    cnf.add_variable(2)
    cnf.add_clause([(True, 2), (False, 1)])
    dimacs = io.StringIO(cnf.dimacs())
    cnf2 = readCNF(dimacs)
    assertCnfEqual(cnf2, cnf)


def test_double_conversion_random():
    cnf = RandomKCNF(4, 10, 100)
    dimacs = io.StringIO(cnf.dimacs())
    cnf2 = readCNF(dimacs)
    assertCnfEqualsIgnoreVariables(cnf, cnf2)


def test_dimacs_subcommand_badinput():
    badformula = io.StringIO("nd jkdh aHej!\n")
    with redirect_stdin(badformula):
        with pytest.raises(CLIError):
            cnfgen(['cnfgen', 'dimacs'], mode='formula')


def test_dimacs_subcommand_goodinput():
    din = """p cnf 5 4
1 -3 5 0
-2 3 -4 0
2 -3 -5 0
2 3 -5 0"""
    with redirect_stdin(io.StringIO(din)):
        dout = cnfgen(['cnfgen', '-q', 'dimacs'], mode='string')
    assert din == dout
