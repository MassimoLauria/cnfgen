#!/usr/bin/env python

from cnfformula.cnf import CNF

from . import TestCNFBase

import random
import itertools

class TestCNF(TestCNFBase) :

    def test_empty(self) :
        F=CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F),[])

    def test_strict_clause_insertion(self):
        F=CNF()
        F.mode_strict()
        F.add_variable("S")
        F.add_variable("T")
        F.add_variable("U")
        self.assertTrue(len(list(F.variables()))==3)
        F.add_clause([(True,"S"),(False,"T")])
        F.add_clause([(True,"T"),(False,"U")])
        self.assertRaises(ValueError, F.add_clause,
                          [(True,"T"),(False,"V")])

    def test_auto_add_variables(self):
        F=CNF()
        F.auto_add_variables = True
        F.add_variable("S")
        F.add_variable("U")
        self.assertTrue(len(list(F.variables()))==2)
        F.add_clause([(True,"S"),(False,"T")])
        self.assertTrue(len(list(F.variables()))==3)
        F.auto_add_variables = False
        F.add_clause([(True,"T"),(False,"U")])
        self.assertRaises(ValueError, F.add_clause,
                          [(True,"T"),(False,"V")])

    def test_literal_repetitions(self):
        F=CNF()
        F.auto_add_variables = True
        F.allow_literal_repetitions = True
        F.add_clause([(True,"S"),(False,"T"),(True,"S")])
        F.allow_literal_repetitions = False
        self.assertRaises(ValueError, F.add_clause,
                          [(False,"T"),(True,"V"),(False,"T")])

    def test_opposite_literals(self):
        F=CNF()
        F.auto_add_variables = True
        F.allow_opposite_literals = True
        F.add_clause([(True,"S"),(False,"T"),(False,"S")])
        F.allow_opposite_literals = False
        self.assertRaises(ValueError, F.add_clause,
                          [(True,"T"),(True,"V"),(False,"T")])


    def test_clause_number(self) :
        F=CNF()
        F.add_clause([(False, 'x')])
        F.add_clause([(True, 'x'), (False, 'y')])
        self.assertEqual(len(F),len(list(F)))
