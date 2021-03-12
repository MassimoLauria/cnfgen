#!/usr/bin/env python

import random
import itertools
import pytest
import io
from cnfgen import CNF


def test_empty():
    F = CNF()
    assert F.debug()
    assert F.number_of_clauses() == 0
    assert F.number_of_variables() == 0


def test_variable_auto_increase():

    F = CNF()
    s = F.new_variable("S")
    u = F.new_variable("U")
    assert F.number_of_variables() == 2

    F.add_clause([1,-3])
    assert F.number_of_variables() == 3

    F.add_clause([3,2])
    assert F.number_of_variables() == 3


def test_dimacs_ascii():
    "CNF should support unicode. This is Python 3 after all."
    cnf = CNF(description='Unicöde string not ascii')
    cnf.new_variable('x')
    cnf.new_variable('ζ')
    cnf.add_clause([1,2])
    cnf.header['extra'] = 'áéíóúàèìòù'
    buffer=io.StringIO()
    cnf.to_file(buffer)
    text = buffer.getvalue()
    byte = text.encode('ascii')
    assert len(byte) == len(text)
