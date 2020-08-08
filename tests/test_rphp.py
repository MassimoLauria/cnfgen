import sys
import pytest

from cnfgen import CNF
from cnfgen import RelativizedPigeonholePrinciple

from cnfgen.clitools import cnfgen, CLIError

from tests.utils import assertUNSAT, assertCnfEqual, assertCnfEqualsDimacs, assertCnfEqualsIgnoreVariables


def test_bad_cliargs_pigeons():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'rphp', -5, 8, 4], mode='string')


def test_bad_cliargs_resting_places():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'rphp', 5, -8, 4], mode='string')


def test_bad_cliargs_holes():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'rphp', 5, 8, -4], mode='string')


def test_bad_args_pigeons():
    with pytest.raises(ValueError):
        RelativizedPigeonholePrinciple(-5, 8, 4)


def test_bad_args_resting_places():
    with pytest.raises(ValueError):
        RelativizedPigeonholePrinciple(5, -8, 4)


def test_bad_args_holes():
    with pytest.raises(ValueError):
        RelativizedPigeonholePrinciple(5, 8, -4)


def test_empty_pigeons():
    dimacs = cnfgen(['cnfgen', '-q', 'rphp', 0, 10, 4], mode='string')
    F = RelativizedPigeonholePrinciple(0, 10, 4)
    assert F.dimacs(export_header=False) == dimacs


def test_empty_holes():
    dimacs = cnfgen(['cnfgen', '-q', 'rphp', 5, 10, 0], mode='string')
    F = RelativizedPigeonholePrinciple(5, 10, 0)
    assert F.dimacs(export_header=False) == dimacs


def test_empty_resting_places():
    dimacs = cnfgen(['cnfgen', '-q', 'rphp', 5, 0, 4], mode='string')
    F = RelativizedPigeonholePrinciple(5, 0, 4)
    assert F.dimacs(export_header=False) == dimacs
