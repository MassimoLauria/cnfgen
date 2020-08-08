#!/usr/bin/env python

import random
import pytest
from cnfgen import RandomKCNF
from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs


def test_only_integer_seed_bad():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '--seed', 'jsfhjakhf', 'randkcnf', 3, 5, 3])


def test_only_integer_seed_good():
    cnfgen(['cnfgen', '--seed', '12', 'randkcnf', 3, 5, 3])


def test_formula_vs_formula():
    F1 = RandomKCNF(3, 25, 60, seed=2311)
    F2 = RandomKCNF(3, 25, 60, seed=2311)
    assertCnfEqual(F1, F2)


def test_formula_vs_cli():
    dimacs = cnfgen(['cnfgen', '-q', '--seed', '2311', 'randkcnf', 3, 20, 40],
                    mode='string')
    random.seed(2311)
    F = RandomKCNF(3, 20, 40)
    assertCnfEqualsDimacs(F, dimacs)
