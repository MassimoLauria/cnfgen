import pytest

from cnfformula import RandomKCNF


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
