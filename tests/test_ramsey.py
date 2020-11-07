import pytest

from cnfgen import PythagoreanTriples
from cnfgen import RamseyNumber
from cnfgen import VanDerWaerden

from cnfgen.clitools import cnfgen, CLIError


def subsets(N, k):
    if k < 0:
        return ValueError
    A = 1
    B = 1
    for i in range(k):
        A *= N
        B *= i + 1
        N -= 1
    return A // B


#
# Test formulas with good args
#
def test_ramsey_3_3_5():
    F = RamseyNumber(3, 3, 5)
    assert len(list(F.variables())) == 10
    assert len(F) == subsets(5, 3) * 2
    assert F.is_satisfiable()[0]


def test_ramsey_3_3_6():
    F = RamseyNumber(3, 3, 6)
    assert len(list(F.variables())) == 15
    assert len(F) == subsets(6, 3) * 2
    assert not F.is_satisfiable()[0]


def test_ptn_0():
    F = PythagoreanTriples(0)
    assert len(list(F.variables())) == 0
    assert len(F) == 0
    assert F.is_satisfiable()[0]


def test_ptn_3():
    F = PythagoreanTriples(3)
    assert len(list(F.variables())) == 3
    assert len(F) == 0
    assert F.is_satisfiable()[0]


def test_ptn_13():
    F = PythagoreanTriples(13)
    assert len(list(F.variables())) == 13
    assert len(F) == 6
    assert F.is_satisfiable()[0]


def test_vdw_9_3_3():
    F = VanDerWaerden(9, 3, 3)
    assert len(list(F.variables())) == 9
    assert not F.is_satisfiable()[0]


def test_vdw_18_4_3():
    F = VanDerWaerden(18, 4, 3)
    assert len(list(F.variables())) == 18
    assert not F.is_satisfiable()[0]


def test_vdw_35_4_4():
    F = VanDerWaerden(35, 4, 4)
    assert len(list(F.variables())) == 35
    assert not F.is_satisfiable()[0]


def test_vdw_8_3_3():
    F = VanDerWaerden(8, 3, 3)
    assert len(list(F.variables())) == 8
    assert F.is_satisfiable()[0]


def test_vdw_17_4_3():
    F = VanDerWaerden(17, 4, 3)
    assert len(list(F.variables())) == 17
    assert F.is_satisfiable()[0]


def test_vdw_34_4_4():
    F = VanDerWaerden(34, 4, 4)
    assert len(list(F.variables())) == 34
    assert F.is_satisfiable()[0]


def test_vdw_15_3_4_5():
    F = VanDerWaerden(15, 3, 4, 5)
    assert len(list(F.variables())) == 45


def test_vdw_15_3_4_5_5():
    F = VanDerWaerden(15, 3, 4, 5, 5)
    assert len(list(F.variables())) == 60


#
# Test formulas with bad args
#


def test_ramsey_bad_value():
    with pytest.raises(ValueError):
        RamseyNumber(-3, 3, 6)
    with pytest.raises(ValueError):
        RamseyNumber(3, -3, 6)
    with pytest.raises(ValueError):
        RamseyNumber(3, 3, -6)


def test_ramsey_bad_type():
    with pytest.raises(TypeError):
        RamseyNumber('aaa', 3, 6)
    with pytest.raises(TypeError):
        RamseyNumber(3, 'bbb', 6)
    with pytest.raises(TypeError):
        RamseyNumber(3, 3, 'ccc')


def test_ptn_bad_value():
    with pytest.raises(ValueError):
        PythagoreanTriples(-3)
    with pytest.raises(ValueError):
        PythagoreanTriples(-1)


def test_ptn_bad_type():
    with pytest.raises(TypeError):
        PythagoreanTriples('aaa')


def test_vdw_bad_types1():
    with pytest.raises(TypeError):
        VanDerWaerden("aaa", 4, 4)


def test_vdw_bad_types2():
    with pytest.raises(TypeError):
        VanDerWaerden(17, "aaa", 4)


def test_vdw_bad_types3():
    with pytest.raises(TypeError):
        VanDerWaerden(17, 4, 'bbbb')


def test_vdw_bad_types4():
    with pytest.raises(TypeError):
        VanDerWaerden(17, 4, 3, 'bbbb')


def test_vdw_bad_types5():
    with pytest.raises(TypeError):
        VanDerWaerden(17, 4, 4, 4, 'bbbb')


#
# Test cli with good args
#


def test_ramsey_3_3_5_cli():
    F = cnfgen(["cnfgen", 'ram', 3, 3, 5], mode='formula')
    assert len(list(F.variables())) == 10
    assert len(F) == subsets(5, 3) * 2
    assert F.is_satisfiable()[0]


def test_ramsey_3_3_6_cli():
    F = cnfgen(["cnfgen", 'ram', 3, 3, 6], mode='formula')
    assert len(list(F.variables())) == 15
    assert len(F) == subsets(6, 3) * 2
    assert not F.is_satisfiable()[0]


def test_ptn_0_cli():
    F = cnfgen(["cnfgen", 'ptn', 0], mode='formula')
    assert len(list(F.variables())) == 0
    assert len(F) == 0
    assert F.is_satisfiable()[0]


def test_ptn_3_cli():
    F = cnfgen(["cnfgen", 'ptn', 3], mode='formula')
    assert len(list(F.variables())) == 3
    assert len(F) == 0
    assert F.is_satisfiable()[0]


def test_ptn_13_cli():
    F = cnfgen(["cnfgen", 'ptn', 13], mode='formula')
    assert len(list(F.variables())) == 13
    assert len(F) == 6
    assert F.is_satisfiable()[0]


def test_vdw_9_3_3_cli():
    F = cnfgen(["cnfgen", 'vdw', 9, 3, 3], mode='formula')
    assert len(list(F.variables())) == 9
    assert not F.is_satisfiable()[0]


def test_vdw_18_4_3_cli():
    F = cnfgen(["cnfgen", 'vdw', 18, 4, 3], mode='formula')
    assert len(list(F.variables())) == 18
    assert not F.is_satisfiable()[0]


def test_vdw_35_4_4_cli():
    F = cnfgen(["cnfgen", 'vdw', 35, 4, 4], mode='formula')
    assert len(list(F.variables())) == 35
    assert not F.is_satisfiable()[0]


def test_vdw_8_3_3_cli():
    F = cnfgen(["cnfgen", 'vdw', 8, 3, 3], mode='formula')
    assert len(list(F.variables())) == 8
    assert F.is_satisfiable()[0]


def test_vdw_17_4_3_cli():
    F = cnfgen(["cnfgen", 'vdw', 17, 4, 3], mode='formula')
    assert len(list(F.variables())) == 17
    assert F.is_satisfiable()[0]


def test_vdw_34_4_4_cli():
    F = cnfgen(["cnfgen", 'vdw', 34, 4, 4], mode='formula')
    assert len(list(F.variables())) == 34
    assert F.is_satisfiable()[0]


def test_vdw_15_3_4_5_cli():
    F = cnfgen(["cnfgen", 'vdw', 15, 3, 4, 5], mode='formula')
    assert len(list(F.variables())) == 45


def test_vdw_15_3_4_5_5_cli():
    F = cnfgen(["cnfgen", 'vdw', 15, 3, 4, 5, 5], mode='formula')
    assert len(list(F.variables())) == 60


#
# Test cli with bad args
#


def test_ramsey_cli_bad_args1():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'ram', -3, 3, 6])


def test_ramsey_cli_bad_args2():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'ram', 3, -3, 6])


def test_ramsey_cli_bad_args3():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'ram', 3, 3, -6])


def test_ptn_cli_bad_args():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'ptn', -10])


def test_vdw_cli_bad_args1():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', 3, 1])


def test_vdw_cli_bad_args2():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', -3, 1, 1])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', 3, -1, 1])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', 3, 1, -1])


def test_vdw_cli_bad_args3():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', 13, 3, 3, -5])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", 'vdw', 13, 3, 3, 5, -2])
