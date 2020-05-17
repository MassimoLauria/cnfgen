from cnfformula import CNF

from cnfformula import OrSubstitution, XorSubstitution, MajoritySubstitution
from cnfformula import AllEqualSubstitution, NotAllEqualSubstitution
from cnfformula import IfThenElseSubstitution, ExactlyOneSubstitution

from tests.utils import assertCnfEqual


def test_or():
    cnf = CNF([[(True, 'x'), (False, 'y')]])
    lift = OrSubstitution(cnf, 3)
    assertCnfEqual(
        lift,
        CNF([
            [(True, '{x}^0'), (True, '{x}^1'), (True, '{x}^2'),
             (False, '{y}^0')],
            [(True, '{x}^0'), (True, '{x}^1'), (True, '{x}^2'),
             (False, '{y}^1')],
            [(True, '{x}^0'), (True, '{x}^1'), (True, '{x}^2'),
             (False, '{y}^2')],
        ]))
    lift2 = OrSubstitution(cnf, 3)
    assertCnfEqual(lift, lift2)


def test_xor():
    cnf = CNF([[(True, 'x'), (False, 'y')]])
    lift = XorSubstitution(cnf, 2)
    assertCnfEqual(
        lift,
        CNF([
            [(True, '{x}^0'), (True, '{x}^1'), (True, '{y}^0'),
             (False, '{y}^1')],
            [(False, '{x}^0'), (False, '{x}^1'), (True, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^0'), (True, '{x}^1'), (False, '{y}^0'),
             (True, '{y}^1')],
            [(False, '{x}^0'), (False, '{x}^1'), (False, '{y}^0'),
             (True, '{y}^1')],
        ]))
    lift2 = XorSubstitution(cnf, 2)
    assertCnfEqual(lift, lift2)


def test_majority():
    cnf = CNF([[(True, 'x'), (False, 'y')]])
    lift = MajoritySubstitution(cnf, 3)
    assertCnfEqual(
        lift,
        CNF([
            [(True, '{x}^0'), (True, '{x}^1'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^1'), (True, '{x}^2'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^2'), (True, '{x}^0'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^0'), (True, '{x}^1'), (False, '{y}^1'),
             (False, '{y}^2')],
            [(True, '{x}^1'), (True, '{x}^2'), (False, '{y}^1'),
             (False, '{y}^2')],
            [(True, '{x}^2'), (True, '{x}^0'), (False, '{y}^1'),
             (False, '{y}^2')],
            [(True, '{x}^0'), (True, '{x}^1'), (False, '{y}^2'),
             (False, '{y}^0')],
            [(True, '{x}^1'), (True, '{x}^2'), (False, '{y}^2'),
             (False, '{y}^0')],
            [(True, '{x}^2'), (True, '{x}^0'), (False, '{y}^2'),
             (False, '{y}^0')],
        ]))
    lift2 = MajoritySubstitution(cnf, 3)
    assertCnfEqual(lift, lift2)


def test_equality():
    cnf = CNF([[(False, 'x'), (True, 'y')]])
    lift = AllEqualSubstitution(cnf, 2)
    assertCnfEqual(
        lift,
        CNF([
            [(True, '{x}^0'), (True, '{x}^1'), (True, '{y}^0'),
             (False, '{y}^1')],
            [(False, '{x}^0'), (False, '{x}^1'), (True, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^0'), (True, '{x}^1'), (False, '{y}^0'),
             (True, '{y}^1')],
            [(False, '{x}^0'), (False, '{x}^1'), (False, '{y}^0'),
             (True, '{y}^1')],
        ]))
    lift2 = AllEqualSubstitution(cnf, 2)
    assertCnfEqual(lift, lift2)


def test_inequality():
    cnf = CNF([[(False, 'x'), (True, 'y')]])
    lift = NotAllEqualSubstitution(cnf, 2)
    assertCnfEqual(
        lift,
        CNF([
            [(True, '{x}^0'), (False, '{x}^1'), (True, '{y}^0'),
             (True, '{y}^1')],
            [(False, '{x}^0'), (True, '{x}^1'), (True, '{y}^0'),
             (True, '{y}^1')],
            [(True, '{x}^0'), (False, '{x}^1'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(False, '{x}^0'), (True, '{x}^1'), (False, '{y}^0'),
             (False, '{y}^1')],
        ]))


def test_inequality_pos_clause():
    cnf = CNF([[(True, 'x')]])
    lift = NotAllEqualSubstitution(cnf, 3)
    assertCnfEqual(
        lift,
        CNF([[(True, '{x}^0'), (True, '{x}^1'), (True, '{x}^2')],
             [(False, '{x}^0'), (False, '{x}^1'), (False, '{x}^2')]]))


def test_eq_vs_neq():
    cnf = CNF([[(False, 'x'), (True, 'y')], [(True, 'z'), (True, 't')],
               [(False, 'u'), (False, 'v')]])
    cnfneg = CNF([[(True, 'x'), (False, 'y')], [(False, 'z'), (False, 't')],
                  [(True, 'u'), (True, 'v')]])
    lifteq = AllEqualSubstitution(cnf, 4)
    liftneq = NotAllEqualSubstitution(cnfneg, 4)
    assertCnfEqual(lifteq, liftneq)


def test_if_then_else():
    cnf = CNF([[(True, 'x'), (False, 'y')]])
    lift = IfThenElseSubstitution(cnf)
    assertCnfEqual(
        lift,
        CNF([
            [(False, '{x}^0'), (True, '{x}^1'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(False, '{x}^0'), (True, '{x}^1'), (True, '{y}^0'),
             (False, '{y}^2')],
            [(True, '{x}^0'), (True, '{x}^2'), (False, '{y}^0'),
             (False, '{y}^1')],
            [(True, '{x}^0'), (True, '{x}^2'), (True, '{y}^0'),
             (False, '{y}^2')],
        ]))
    lift2 = IfThenElseSubstitution(cnf)
    assertCnfEqual(lift, lift2)


def test_exactly_one():
    cnf = CNF([[(True, 'x'), (False, 'y')]])
    lift = ExactlyOneSubstitution(cnf, 2)
    lift2 = ExactlyOneSubstitution(cnf, 2)
    assertCnfEqual(lift, lift2)
