import pytest

from cnfgen import RandomKCNF
from cnfgen.clitools import cnfgen, CLIError


def test_empty_cnf():
    F = RandomKCNF(0, 0, 0)
    assert list(F.variables()) == []
    assert len(F) == 0


def test_empty_cnf_with_vars():
    F = RandomKCNF(0, 6, 0)
    assert list(F.variables()) == ["x_1", "x_2", "x_3", "x_4", "x_5", "x_6"]
    assert len(F) == 0


def test_random_cnf_medium():
    F = RandomKCNF(3, 10, 50)
    assert list(F.variables()) == [
        "x_1", "x_2", "x_3", "x_4", "x_5", "x_6", "x_7", "x_8", "x_9", "x_10"
    ]
    assert len(F) == 50
    for c in F:
        assert len(c) == 3


def test_all_clauses():
    max_clauses = 2**3 * 5 * 4 * 3 // (1 * 2 * 3)
    F = RandomKCNF(3, 5, max_clauses)
    assert len(F) == max_clauses


def test_too_many_clauses():
    max_clauses = 2**3 * 5 * 4 * 3 // (1 * 2 * 3)
    with pytest.raises(ValueError):
        RandomKCNF(3, 5, max_clauses + 1)


def test_too_wide():
    with pytest.raises(ValueError):
        RandomKCNF(10, 5, 1)


def test_negative_width():
    with pytest.raises(ValueError):
        RandomKCNF(-1, 5, 1)


def test_negative_variables():
    with pytest.raises(ValueError):
        RandomKCNF(3, -1, 1)


def test_negative_clauses():
    with pytest.raises(ValueError):
        RandomKCNF(3, 5, -1)


def test_random_cnf_planted():
    planted = [{"x_1": True, "x_2": False, "x_3": True}]
    F = RandomKCNF(3, 3, 7, planted_assignments=planted)
    for c in F:
        assert len(c) == 3


def test_random_cnf_planted_2():
    planted = [{
        "x_1": True,
        "x_2": False,
        "x_3": True,
        "x_4": False,
        "x_5": True,
        "x_6": True
    }]
    F = RandomKCNF(3, 6, 10, planted_assignments=planted)
    for c in F:
        assert len(c) == 3
    assert len(F) == 10


def test_randomkcnf_cnfgen():
    cnfgen(["cnfgen", 'randkcnf', 4, 6, 10])


def test_randomkcnf_cnfgen_planted():
    cnfgen(["cnfgen", 'randkcnf', 3, 6, 10, '-p'])


def test_randomkcnf_cnfgen_planted_bad():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'randkcnf', 3, 3, 8, '-p'])
