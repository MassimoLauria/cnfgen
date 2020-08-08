#!/usr/bin/env python3

import sys
import pytest

from cnfgen.clitools import cnfgen
from cnfgen.clitools import get_formula_helpers, CLIError


def test_no_formula():

    msg = "ERROR: You did not tell which formula you wanted to generate."

    with pytest.raises(CLIError) as e:
        cnfgen(['cnfgen'])

    assert msg in str(e.value)


def test_invalid_formula():

    msg = "invalid choice"

    with pytest.raises(CLIError) as e:
        cnfgen(['cnfgen', 'spam'])

    assert msg in str(e.value)


def test_invalid_formula_help():

    msg = "invalid choice"

    with pytest.raises(CLIError) as e:
        cnfgen(['cnfgen', 'spam', '-h'])

    assert msg in str(e.value)


def test_cnfgen_help():
    with pytest.raises(SystemExit) as se:
        cnfgen(["cnfgen", "-h"])

    assert se.value.code == 0


def test_subformulas_help():
    subcommands = get_formula_helpers()
    for sc in subcommands:

        with pytest.raises(SystemExit) as se:
            cnfgen(["cnfgen", sc.name, "-h"])

        assert se.value.code == 0
