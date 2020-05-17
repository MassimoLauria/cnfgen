#!/usr/bin/env python3

from cnfgen.cmdline import get_formula_helpers
from cnfgen.cmdline import get_transformation_helpers


def test_find_formula_helpers():
    """All formula families are detected."""
    subcommands = get_formula_helpers()
    assert len(subcommands) == 30


def test_find_formula_examples():
    """All formula families are detected."""
    subcommands = get_formula_helpers()
    assert 'php' in subcommands
    assert 'tseitin' in subcommands


def test_find_transformation_helpers():
    """All formula transformations are detected."""
    transformations = get_transformation_helpers()
    assert len(transformations) == 13


def test_find_transformation_examples():
    """All formula transformations are detected."""
    transformations = get_transformation_helpers()
    assert 'xor' in transformations
    assert 'maj' in transformations
