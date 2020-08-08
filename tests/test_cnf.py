#!/usr/bin/env python

import random
import itertools
import pytest

from cnfgen import CNF


def test_empty():
    F = CNF()
    assert F.debug()
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
    cnf = CNF(description='Unicöde string not ascii')
    cnf.add_variable('x')
    cnf.add_variable('ζ')
    cnf.add_clause([(True, "x"), (False, "ζ")])
    text = cnf.dimacs(extra_text='áéíóúàèìòù')
    byte = text.encode('ascii')
    assert len(byte) == len(text)
