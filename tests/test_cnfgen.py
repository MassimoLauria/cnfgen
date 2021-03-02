#!/usr/bin/env python3

import os
import sys
import pytest

from cnfgen.clitools import cnfgen
from cnfgen.clitools import get_formula_helpers, CLIError

from cnfgen.clitools import redirect_stdin
from contextlib import redirect_stdout
from io import StringIO

from cnfgen.formula.cnfio import guess_output_format


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


@pytest.mark.parametrize("subcommand", get_formula_helpers())
def test_subformulas_help(subcommand):
    with pytest.raises(SystemExit) as se:
        cnfgen(["cnfgen", subcommand.name, "-h"])
    assert se.value.code == 0


testdata = [('out.tex', 'latex', 'latex'),
            ('out.tex', 'dimacs', 'dimacs'),
            ('out.tex', None, 'latex'),
            ('out.cnf', 'latex', 'latex'),
            ('out.cnf', 'dimacs', 'dimacs'),
            ('out.cnf', None, 'dimacs'),
            (sys.stdout, 'latex', 'latex'),
            (sys.stdout, 'dimacs', 'dimacs'),
            (sys.stdout, None, 'dimacs')]


@pytest.mark.parametrize("name,fformat,expected", testdata)
def test_fileformat_guess(name, fformat, expected):
    assert guess_output_format(name, fformat) == expected



def find_string_in_file(lines, string):
    for line in lines:
        if string in line:
            return True
    return False


@pytest.mark.parametrize("name,fformat,expected", testdata)
def test_fileformat_file(name, fformat, expected, tmpdir):

    cmdline = ['cnfgen']
    teststring = 'p cnf' if expected == 'dimacs' else '\\maketitle'

    if name != sys.stdout:
        path = tmpdir.join(name)
        cmdline.append('-o')
        cmdline.append(path)

    if fformat is not None:
        cmdline.append('-of')
        cmdline.append(fformat)
    cmdline.extend(['php', '2', '1'])

    if name == sys.stdout:
        output = StringIO()
        with redirect_stdout(output):
            cnfgen(cmdline)
        lines = output.getvalue().split('\n')
    else:
        cnfgen(cmdline)
        with open(path, 'r') as output:
            lines = output.readlines()

    assert find_string_in_file(lines, teststring)
