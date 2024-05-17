import pytest

from cnfgen import CNF

from cnfgen.transformations.substitutions import OrSubstitution, XorSubstitution, MajoritySubstitution
from cnfgen.transformations.substitutions import AllEqualSubstitution, NotAllEqualSubstitution
from cnfgen.transformations.substitutions import IfThenElseSubstitution
from cnfgen.transformations.substitutions import ExactlyKSubstitution, ExactlyOneSubstitution
from cnfgen.transformations.substitutions import FlipPolarity
from cnfgen.clitools import cnfgen, CLIError

from tests.utils import assertCnfEqual,assertCnfEqualsIgnoreVariables


def test_or():
    cnf = CNF([[1,-2]])
    lift = OrSubstitution(cnf, 3)
    expected = CNF([
        [1, 2, 3, -4],
        [1, 2, 3, -5],
        [1, 2, 3, -6]])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()

def test_xor():
    cnf = CNF([[1, -2]])
    lift = XorSubstitution(cnf, 2)
    expected = CNF([
            [1, 2, 3, -4],
            [1, 2, -3, 4],
            [-1, -2, 3, -4],
            [-1, -2, -3, 4]])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_majority():
    cnf = CNF([[1, -2]])
    lift = MajoritySubstitution(cnf, 3)
    expected = CNF([
            [1, 2, -4, -5],
            [1, 2, -4, -6],
            [1, 2, -5, -6],
            [1, 3, -4, -5],
            [1, 3, -4, -6],
            [1, 3, -5, -6],
            [2, 3, -4, -5],
            [2, 3, -4, -6],
            [2, 3, -5, -6]])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_equality():
    cnf = CNF([[-1, +2]])
    lift = AllEqualSubstitution(cnf, 2)
    expected = CNF([
        [+1, +2, +3, -4],
        [+1, +2, -3, +4],
        [-1, -2, +3, -4],
        [-1, -2, -3, +4],
    ])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_inequality():
    cnf = CNF([[-1, +2]])
    lift = NotAllEqualSubstitution(cnf, 2)
    expected = CNF([
        [+1, -2, +3, +4],
        [+1, -2, -3, -4],
        [-1, +2, +3, +4],
        [-1, +2, -3, -4]])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()

def test_labels_escaping():
    cnf = CNF()
    cnf.new_block(4, label='x_{{{}}}')
    cnf.add_clause([-1,-2,-3])
    lift = XorSubstitution(cnf, 2)
    assert lift.number_of_variables() == 8
    assert len(lift.clauses()) == 8



def test_inequality_pos_clause():
    cnf = CNF([[1]])
    lift = NotAllEqualSubstitution(cnf, 3)
    expected = CNF([[1, 2, 3], [-1, -2, -3]])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_eq_vs_neq():
    cnf = CNF([[-1, 2], [3, 4], [-5, -6]])
    cnfneg = FlipPolarity(cnf)
    lifteq = AllEqualSubstitution(cnf, 4)
    liftneq = NotAllEqualSubstitution(cnfneg, 4)
    assert lifteq.number_of_variables() == liftneq.number_of_variables()
    assert lifteq.clauses() == liftneq.clauses()


def test_if_then_else():
    cnf = CNF([[1, -2]])
    lift = IfThenElseSubstitution(cnf)
    expected = CNF([
        [-1, +3, -2, -4],
        [-1, +3, +2, -6],
        [+1, +5, -2, -4],
        [+1, +5, +2, -6],
    ])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_exactly_one():
    cnf = CNF([[1, -2]])
    lift = ExactlyOneSubstitution(cnf, 3)
    expected = CNF([
        [-1, -2, -4, 5, 6],
        [-1, -2,  4,-5, 6],
        [-1, -2, +4, 5,-6],
        [-1, -3, -4, 5, 6],
        [-1, -3,  4,-5, 6],
        [-1, -3, +4, 5,-6],
        [-2, -3, -4, 5, 6],
        [-2, -3,  4,-5, 6],
        [-2, -3, +4, 5,-6],
        [1, 2, 3, -4, 5, 6],
        [1, 2, 3,  4,-5, 6],
        [1, 2, 3, +4, 5,-6],
    ])
    assert lift.number_of_variables() == expected.number_of_variables()
    assert lift.clauses() == expected.clauses()


def test_cli_xorcompression_good1():
    F = cnfgen(["cnfgen", 'php', 7, 5, '-T', 'xorcomp', 12, 3], mode='formula')
    assert len(list(F.variables())) == 12


def test_cli_xorcompression_good2():
    F = cnfgen(["cnfgen", 'php', 7, 5, '-T', 'xorcomp', 'glrd', 35, 12, 3],
               mode='formula')
    assert len(list(F.variables())) == 12


def test_cli_xorcompression_bad():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'php', 7, 5, '-T', 'xorcomp', 'glrd', 30, 12, 3],
               mode='formula')


def test_cli_majcompression_good1():
    F = cnfgen(["cnfgen", 'php', 7, 5, '-T', 'majcomp', 12, 3], mode='formula')
    assert len(list(F.variables())) == 12



def test_cli_majcompression_good2():
    F = cnfgen(["cnfgen", 'php', 7, 5, '-T', 'majcomp', 'glrd', 35, 12, 3],
               mode='formula')
    assert len(list(F.variables())) == 12


def test_cli_majcompression_bad():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'php', 7, 5, '-T', 'majcomp', 'glrd', 30, 12, 3],
               mode='formula')

def test_cli_op_xor():
    "Test against bug #114 in the repo due to label escaping"
    F = cnfgen(["cnfgen", 'op', 10, 3, '-T', 'xor', 2],
               mode='formula')
    assert True
