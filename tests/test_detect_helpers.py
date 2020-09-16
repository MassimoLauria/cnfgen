#!/usr/bin/env python3

from cnfgen.clitools import get_formula_helpers
from cnfgen.clitools import get_transformation_helpers


def test_find_formula_helpers():
    """All formula families are detected."""
    subcommands = get_formula_helpers()
    assert len(subcommands) == 31


def test_find_formula_examples():
    """All formula families are detected."""
    names = [fh.name for fh in get_formula_helpers()]
    assert 'php' in names
    assert 'iso' in names
    assert 'tseitin' in names
    assert 'dimacs' in names
    assert 'ec' in names
    assert 'randkcnf' in names
    assert 'subsetcard' in names
    assert 'rphp' in names


def test_find_transformation_helpers():
    """All formula transformations are detected."""
    transformations = get_transformation_helpers()
    assert len(transformations) == 17


def test_find_transformation_examples():
    """All formula transformations are detected."""
    names = [fh.name for fh in get_transformation_helpers()]
    assert 'xor' in names
    assert 'maj' in names
    assert 'or' in names
