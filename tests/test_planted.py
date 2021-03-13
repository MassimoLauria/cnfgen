import pytest

from cnfgen import CNF
from cnfgen import RandomKCNF

from tests.utils import assertCnfEqual


def test_not_planted():
    F = RandomKCNF(4, 10, 20, seed=2311)
    G = RandomKCNF(4, 10, 20, seed=2311, planted_assignments=[])
    assertCnfEqual(F, G)


def test_one():
    assign = [[1,-2]]
    F = RandomKCNF(2, 2, 3, planted_assignments=assign)
    G = CNF([[+1, -2],
             [-1, -2],
             [+1, +2]])
    assertCnfEqual(F, G)


def test_most():
    ass = [[+1, -2],
           [-1, -2],
           [+1, +2]]
    F = RandomKCNF(2, 2, 1, planted_assignments=ass)
    G = CNF([[1, -2]])
    assertCnfEqual(F, G)


def test_all():
    ass = [[+1, -2],
           [-1, -2],
           [+1, +2],
           [-1, +2]]
    with pytest.raises(ValueError):
        RandomKCNF(2, 2, 1, planted_assignments=ass)
