#!/usr/bin/env python

import unittest
import textwrap
import random
import itertools

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
    that two CNFs are actually the same, plus some utility function to
    produce CNFs to test.
    """
    def assertCnfEqual(self,cnf1,cnf2):
        self.assertSetEqual(set(cnf1.variables()),set(cnf2.variables()))
        self.assertSetSetEqual(cnf1,cnf2)

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
        print cnf1._constraints
        print cnf2._constraints
        self.assertSetEqual(
            set(cnf1._enumerate_compressed_clauses()),
            set(cnf2._enumerate_compressed_clauses()))

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

    @staticmethod
    def cnf_from_variables_and_clauses(variables, clauses) :
        cnf = CNF()
        for variable in variables :
            cnf.add_variable(variable)
        for clause in clauses :
            cnf.add_clause(clause)
        return cnf

    @staticmethod
    def sorted_cnf(clauses) :
        return TestCNFBase.cnf_from_variables_and_clauses(
            sorted(set(variable for polarity,variable in itertools.chain(*clauses))),
            clauses)

    @staticmethod
    def random_cnf(width, num_variables, num_clauses) :
        return TestCNFBase.cnf_from_variables_and_clauses(xrange(1,num_variables+1), [
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
