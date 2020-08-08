#!/usr/bin/env python

import pytest
import textwrap

from cnfformula import some_solver_installed
from cnfgen.clitools import redirect_stdin
from contextlib import redirect_stdout

__all__ = [
    'assertCnfEqual', "assertCnfEqualsDimacs",
    "assertCnfEqualsIgnoreVariables", "assertSAT", "assertUNSAT",
    'redirect_stdin', "redirect_stdout", 'example_filename'
]


def example_filename(filename):
    import os.path

    this_dir = os.path.dirname(os.path.abspath(__file__))
    absfilename = os.path.join(this_dir, 'testdata', filename)

    if not os.path.isfile(absfilename):
        raise ValueError("Test data file {} is missing.".format(filename))
    else:
        return absfilename


def assertCnfEqual(cnf1, cnf2):
    # test whether variable sets are the same
    vars1 = set(cnf1.variables())
    vars2 = set(cnf2.variables())

    Delta1 = list(str(x) for x in vars1 - vars2)
    Delta2 = list(str(x) for x in vars2 - vars1)
    if len(Delta1) + len(Delta2) > 0:
        raise AssertionError("The two CNFs have different variable sets.\n"
                             " - In first and not in second: {}\n"
                             " - In second but not in first: {}".format(
                                 " ".join(Delta1), " ".join(Delta2)))

    # test whether clause sets are the same
    clauses1 = set(frozenset(x) for x in cnf1.clauses())
    clauses2 = set(frozenset(x) for x in cnf2.clauses())

    Delta1 = list(str(list(x)) for x in clauses1 - clauses2)
    Delta2 = list(str(list(x)) for x in clauses2 - clauses1)
    if len(Delta1) + len(Delta2) > 0:
        raise AssertionError("The two CNFs have different clause sets.\n"
                             " - In first and not in second: {}\n"
                             " - In second but not in first: {}".format(
                                 " ".join(Delta1), " ".join(Delta2)))


def assertCnfEqualsDimacs(cnf, dimacs):
    dimacs = textwrap.dedent(dimacs)
    dimacs = dimacs.strip()
    output = cnf.dimacs(export_header=False)
    output = output.strip()
    assert output == dimacs


def assertCnfEqualsIgnoreVariables(cnf1, cnf2):
    assert len(list(cnf1.variables())) == len(list(cnf2.variables()))
    assert set(cnf1._clauses) == set(cnf2._clauses)


def assertSAT(formula):
    if some_solver_installed():
        result, _ = formula.is_satisfiable()
        if not result:
            raise AssertionError(
                "Formula {} is unexpectedly UNSAT".format(formula))
    else:
        pytest.skip("No usable solver found.")


def assertUNSAT(formula):
    if some_solver_installed():
        result, _ = formula.is_satisfiable()
        if result:
            raise AssertionError(
                "Formula {} is unexpectedly SAT".format(formula))
    else:
        pytest.skip("No usable solver found.")
