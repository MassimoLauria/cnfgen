#!/usr/bin/env python

import cnfformula

from . import TestCNFBase

import random
import itertools

class TestCNF(TestCNFBase) :

    @staticmethod
    def cnf_from_variables_and_clauses(variables, clauses) :
        cnf = cnfformula.CNF()
        for variable in variables :
            cnf.add_variable(variable)
        for clause in clauses :
            cnf.add_clause(clause)
        return cnf

    @staticmethod
    def sorted_cnf(clauses) :
        return TestCNF.cnf_from_variables_and_clauses(
            sorted(set(variable for polarity,variable in itertools.chain(*clauses))),
            clauses)

    @staticmethod
    def random_cnf(width, num_variables, num_clauses) :
        return TestCNF.cnf_from_variables_and_clauses(xrange(1,num_variables+1), [
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
    def test_empty(self) :
        F=cnfformula.CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

    def test_safe_clause_insetion(self):
        F=cnfformula.CNF()
        F.add_variable("S")
        F.add_variable("U")
        F.add_clause([(True,"S"),(False,"T")])
        self.assertTrue(len(list(F.variables())),2)
        F.add_clause([(True,"T"),(False,"U")],strict=True)
        self.assertTrue(len(list(F.variables())),3)
        self.assertRaises(ValueError, F.add_clause,
                          [(True,"T"),(False,"V")],strict=True)
