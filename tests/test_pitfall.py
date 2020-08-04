import pytest
import random

from cnfformula import PitfallFormula
from cnfgen import cnfgen, CLIError
from cnfgen.cmdline import get_formula_helpers


def test_helper_exists():
    names = [fh.name for fh in get_formula_helpers()]
    assert 'pitfall' in names


def test_bad_cmd_line():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", -8, 3, 10, 10, 2])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", 8, -3, 10, 10, 2])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", 8, 3, -10, 10, 2])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", 8, 3, 10, -10, 2])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", 8, 3, 10, 10, -2])
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "pitfall", 8, 3, 10, 10, 3])


def test_bad_args():
    with pytest.raises(ValueError):
        PitfallFormula(-8, 3, 10, 10, 2)
    with pytest.raises(ValueError):
        PitfallFormula(8, -3, 10, 10, 2)
    with pytest.raises(ValueError):
        PitfallFormula(8, 3, -10, 10, 2)
    with pytest.raises(ValueError):
        PitfallFormula(8, 3, 10, -10, 2)
    with pytest.raises(ValueError):
        PitfallFormula(8, 3, 10, 10, -2)
    with pytest.raises(ValueError):
        PitfallFormula(8, 3, 10, 10, 3)


def test_good_args():
    PitfallFormula(8, 3, 10, 10, 2)


def test_cmd_line():
    cnfgen(["cnfgen", "-q", "pitfall", 5, 2, 6, 6, 4])


def test_no_regular_graph():
    # There is not 3-regular graph on 9 vertices
    with pytest.raises(ValueError):
        PitfallFormula(9, 3, 10, 10, 2)
    # There is not 9-regular graph on 3 vertices
    with pytest.raises(ValueError):
        PitfallFormula(3, 9, 10, 10, 2)


def test_lib_vs_cli():
    """Comparison between command line and library

To avoid mismatches in the header, we compare the dimacs output
without the comments.
"""
    args = ["cnfgen", "-q", "pitfall", 5, 2, 4, 4, 2]
    random.seed(42)
    F = PitfallFormula(5, 2, 4, 4, 2)
    lib = F.dimacs(export_header=False)
    random.seed(42)
    cli = cnfgen(args, mode='string')
    assert lib == cli
