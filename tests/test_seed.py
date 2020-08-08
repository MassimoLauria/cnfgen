#!/usr/bin/env python

import random
import pytest
from cnfgen import RandomKCNF
from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs

seed_2311 = """
p cnf 7 6
-2 3 4 0
2 3 -7 0
1 -2 6 0
-2 3 -7 0
-2 -3 -5 0
2 -4 -5 0
""".strip()

seed_46512 = """
p cnf 10 20
-2 8 0
1 6 0
-3 4 0
1 10 0
-4 8 0
-3 -5 0
2 -4 0
7 8 0
1 9 0
-1 -3 0
5 -8 0
-4 7 0
1 -9 0
9 10 0
-5 -6 0
-6 9 0
5 10 0
4 -6 0
5 8 0
-7 -9 0
""".strip()


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


def test_formula_vs_seed_2311():
    F1 = RandomKCNF(3, 7, 6, seed=2311)
    dimacs = F1.dimacs(export_header=False)
    assert dimacs == seed_2311.strip()


def test_cli_vs_seed_2311():
    dimacs = cnfgen(['cnfgen', '-q', '--seed', 2311, 'randkcnf', 3, 7, 6],
                    mode='string')
    assert dimacs == seed_2311.strip()


def test_formula_vs_seed_46512():
    F1 = RandomKCNF(2, 10, 20, seed=46512)
    dimacs = F1.dimacs(export_header=False)
    assert dimacs == seed_46512


def test_cli_vs_seed_46512():
    dimacs = cnfgen(['cnfgen', '-q', '--seed', 46512, 'randkcnf', 2, 10, 20],
                    mode='string')
    assert dimacs == seed_46512
