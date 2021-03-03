import sys
import pytest

from cnfgen import CliqueColoring
from cnfgen.clitools import cnfgen

from tests.utils import assertSAT, assertUNSAT


def test_5wheel():
    F = CliqueColoring(6, 3, 4)
    assertSAT(F)


def test_unsat():
    F = CliqueColoring(6, 4, 3)
    assertUNSAT(F)

def test_zero_n():
    F = CliqueColoring(0, 4, 3)
    assertUNSAT(F)

def test_zero_k():
    F = CliqueColoring(6, 0, 3)
    assertSAT(F)

def test_zero_c():
    F = CliqueColoring(6, 4, 0)
    assertUNSAT(F)

def test_one_n():
    F = CliqueColoring(1, 1, 1)
    assertSAT(F)

def test_one_k():
    F = CliqueColoring(6, 1, 3)
    assertSAT(F)

def test_one_c():
    F = CliqueColoring(6, 4, 1)
    assertUNSAT(F)

@pytest.mark.parametrize("n", range(4, 6))
def test_k4_c3(n):
    parameters = ["cnfgen", "-q", "cliquecoloring", str(n), '4', '3']
    F = CliqueColoring(n, 4, 3)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert cli == lib


@pytest.mark.parametrize("n", range(4, 6))
def test_k3_c4(n):
    parameters = ["cnfgen", "-q", "cliquecoloring", str(n), '3', "4"]
    F = CliqueColoring(n, 3, 4)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert cli == lib
