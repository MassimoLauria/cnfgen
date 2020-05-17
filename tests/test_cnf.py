#!/usr/bin/env python

import random
import itertools
import pytest

from cnfformula import CNF

# class TestCNF():
#     @staticmethod
#     def cnf_from_variables_and_clauses(variables, clauses):
#         cnf = CNF()
#         for variable in variables:
#             cnf.add_variable(variable)
#         for clause in clauses:
#             cnf.add_clause(clause)
#         return cnf

#     @staticmethod
#     def sorted_cnf(clauses):
#         return TestCNF.cnf_from_variables_and_clauses(
#             sorted(
#                 set(variable
#                     for polarity, variable in itertools.chain(*clauses))),
#             clauses)

#     @staticmethod
#     def random_cnf(width, num_variables, num_clauses):
#         return TestCNF.cnf_from_variables_and_clauses(
#             range(1, num_variables + 1),
#             [[(random.choice([True, False]), x + 1)
#               for x in random.sample(range(num_variables), width)]
#              for C in range(num_clauses)])


def test_empty():
    F = CNF()
    assert F._check_coherence()
    assert list(F.variables()) == []
    assert list(F.clauses()) == []


def test_safe_clause_insertion():

    F = CNF()
    F.add_variable("S")
    F.add_variable("U")
    assert len(list(F.variables())) == 2

    F.add_clause([(True, "S"), (False, "T")])
    assert len(list(F.variables())) == 3

    F.add_clause([(True, "T"), (False, "U")], strict=True)
    assert len(list(F.variables())) == 3

    with pytest.raises(ValueError):
        F.add_clause([(True, "T"), (False, "V")], strict=True)


def test_dimacs_ascii():
    "CNF should support unicode. This is Python 3 after all."
    cnf = CNF(header='Unicöde string not ascii')
    cnf.add_variable('x')
    cnf.add_variable('ζ')
    cnf.add_clause([(True, "x"), (False, "ζ")])
    text = cnf.dimacs(extra_text='áéíóúàèìòù')
    byte = text.encode('ascii')
    assert len(byte) == len(text)
