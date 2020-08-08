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


def test_k4_c3():
    for n in range(4, 6):
        parameters = ["cnfgen", "-q", "cliquecoloring", str(n), '4', '3']
        F = CliqueColoring(n, 4, 3)
        lib = F.dimacs(export_header=False)
        cli = cnfgen(parameters, mode='string')
        assert cli == lib


def test_k3_c4():
    for n in range(4, 6):
        parameters = ["cnfgen", "-q", "cliquecoloring", str(n), '3', "4"]
        F = CliqueColoring(n, 3, 4)
        lib = F.dimacs(export_header=False)
        cli = cnfgen(parameters, mode='string')
        assert cli == lib
