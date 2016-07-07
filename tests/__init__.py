#!/usr/bin/env python

import unittest
import textwrap

from cnfformula import CNF
from cnfformula.utils.solver import is_satisfiable, have_satsolver


def example_filename(filename):
    import os
    import os.path
    absfilename = os.path.join(os.getcwd(),'tests','testdata',filename)
    if not os.path.isfile(absfilename):
        raise ValueError("Test data file {} is missing.".format(filename))
    else:
        return absfilename

class TestCNFBase(unittest.TestCase):
    """Base class for the test suite.

    It just implements some additional asserting features like testing
    that two CNFs are actually the same.
    """
    def assertCnfEqual(self,cnf1,cnf2):
        self.assertSetEqual(set(cnf1.variables()),set(cnf2.variables()))
        self.assertSetSetEqual(cnf1.clauses(),cnf2.clauses())

    def assertSetSetEqual(self,list1,list2):
        set1=set(frozenset(x) for x in list1)
        set2=set(frozenset(x) for x in list2)
        self.assertSetEqual(set1,set2)

    def assertCnfEqualsDimacs(self, cnf, dimacs):
        dimacs = textwrap.dedent(dimacs)
        dimacs = dimacs.rstrip('\n')
        output = cnf.dimacs(export_header=False)
        output = output.rstrip('\n')
        self.assertEqual(output,dimacs)

    def assertCnfEquivalentModuloVariables(self, cnf1, cnf2):
        self.assertSetEqual(set(cnf1._clauses), set(cnf2._clauses))

    def assertSAT(self, formula):
        if have_satsolver():
            result, _ = is_satisfiable(formula)
            assert result
        else:
            self.skipTest("No usable solver found.")

    def assertUNSAT(self, formula):
        if have_satsolver():
            result, _ = is_satisfiable(formula)
            assert not result
        else:
            self.skipTest("No usable solver found.")
