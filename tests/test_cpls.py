import pytest

from cnfgen import CPLSFormula
from cnfgen.clitools import cnfgen, CLIError
from cnfgen.clitools import get_formula_helpers


def test_helper_exists():
    names = [fh.name for fh in get_formula_helpers()]
    assert 'cpls' in names


def test_bad_cmd_line():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "cpls", -3, 4, 4])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "cpls", 3, -4, 4])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "cpls", 3, 4, -4])


def test_bad_cmd_line_pow2():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "cpls", 3, 7, 8])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "cpls", 3, 8, 7])


def test_bad_args():
    with pytest.raises(ValueError):
        CPLSFormula(-3, 4, 4)
    with pytest.raises(ValueError):
        CPLSFormula(3, -4, 4)
    with pytest.raises(ValueError):
        CPLSFormula(3, 4, -4)


def test_bad_args_pow2():
    with pytest.raises(ValueError):
        CPLSFormula(3, 7, 8)
    with pytest.raises(ValueError):
        CPLSFormula(3, 8, 7)
    with pytest.raises(ValueError):
        CPLSFormula(3, 7, 7)


def test_good_args():
    CPLSFormula(3, 4, 4)


def test_cmd_line():
    cnfgen(["cnfgen", "-q", "cpls", 3, 4, 8])


def test_lib_vs_cli():
    """Comparison between command line and library

To avoid mismatches in the header, we compare the dimacs output
without the comments.
"""
    args = ["cnfgen", "-q", "cpls", 3, 4, 4]
    F = CPLSFormula(3, 4, 4)
    lib = F.to_dimacs()
    cli = cnfgen(args, mode='string')
    assert lib == cli
