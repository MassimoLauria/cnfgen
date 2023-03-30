import pytest

from cnfgen import RandomKXOR
from cnfgen.clitools import cnfgen, CLIError
from cnfgen.families.randomkxor import parity_satisfied


data=[
    [[2,4],1,  [1,2,4], False],
    [[2,4],1,  [1,2,3,-4], True],
    [[],1, [1,3,-4], False],
    [[2,2],0, [1,2], True],
    [[1,2],0, [1,2,-3], True],
    [[],0, [1,2,4], True]
]

@pytest.mark.parametrize('X,b,assign, issat',data)
def test_parity_sat(X,b,assign,issat):
    assert parity_satisfied(X,b,[assign]) == issat

def test_empty_kxor():
    F = RandomKXOR(0, 0, 0)
    assert F.number_of_variables() == 0
    assert len(F) == 0


def test_empty_kxor_with_vars():
    F = RandomKXOR(0, 6, 0)
    assert F.number_of_variables() == 6
    assert len(F) == 0


def test_random_XOR_medium():
    F = RandomKXOR(3, 10, 50)
    assert F.number_of_variables() == 10
    assert len(F) == 4*50
    for c in F:
        assert len(c) == 3


def test_all_parities():
    max_parities = 2 * 5 * 4 * 3 // (1 * 2 * 3)
    F = RandomKXOR(3, 5, max_parities)
    assert len(F) == max_parities*4

def test_all_parities_2():
    max_parities = 2 * 6 * 5 * 4 * 3 // (1 * 2 * 3 * 4)
    F = RandomKXOR(4, 6, max_parities)
    assert len(F) == max_parities*8

def test_too_many_parities():
    max_parities = 2 * 5 * 4 * 3 // (1 * 2 * 3)
    with pytest.raises(ValueError):
        RandomKXOR(3, 5, max_parities + 1)


def test_too_wide():
    with pytest.raises(ValueError):
        RandomKXOR(10, 5, 1)


def test_negative_width():
    with pytest.raises(ValueError):
        RandomKXOR(-1, 5, 1)


def test_negative_variables():
    with pytest.raises(ValueError):
        RandomKXOR(3, -1, 1)


def test_negative_parities():
    with pytest.raises(ValueError):
        RandomKXOR(3, 5, -1)


def test_random_xor_planted():
    planted = [[1,-2,3]]
    F = RandomKXOR(3, 3, 1, planted_assignments=planted)
    for c in F:
        assert len(c) == 3


def test_random_kxor_planted_2():
    planted = [[1, -2, 3, -4, 5, 6]]
    F = RandomKXOR(3, 6, 10, planted_assignments=planted)
    for c in F:
        assert len(c) == 3
    assert len(F) == 10*4


def test_randomkxor_cnfgen():
    cnfgen(["cnfgen", 'randkxor', 4, 6, 10])


def test_randomkxor_cnfgen_planted():
    cnfgen(["cnfgen", 'randkxor', 3, 6, 10, '-p'])


def test_randomkxor_cnfgen_planted_bad():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'randkxor', 3, 3, 2, '-p'])
