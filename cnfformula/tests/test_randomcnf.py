from cnfformula import RandomKCNF
from cnfformula.families.randomformulas import all_clauses

from . import TestCNFBase

class TestRandomCNF(TestCNFBase) :
    def check_random_cnf(self,width,numvariables,numclauses) :
        F = RandomKCNF(width,numvariables,numclauses)
        self.assertListEqual(list(F.variables()),
                             ['x_{0}'.format(i) for i in range(1,numvariables+1)])
        self.assertEqual(len(F),numclauses)
        self.assertEqual(len(set(frozenset(x) for x in F.clauses())),numclauses)

    def test_empty_cnf(self) :
        self.check_random_cnf(0,0,0)

    def test_empty_cnf_with_vars(self) :
        self.check_random_cnf(0,10,0)

    def test_random_cnf_medium(self) :
        self.check_random_cnf(3,10,50)

    def test_full(self):
        self.check_random_cnf(3,5,5*4*3/(1*2*3)*2**3)

    def test_too_full(self):
        with self.assertRaises(ValueError):
            RandomKCNF(3,5,5*4*3/(1*2*3)*2**5+1)

    def test_too_wide(self):
        with self.assertRaises(ValueError):
            RandomKCNF(10,5,1)

    def test_negative_width(self):
        with self.assertRaises(ValueError):
            RandomKCNF(-1,5,1)

    def test_negative_variables(self):
        with self.assertRaises(ValueError):
            RandomKCNF(3,-1,1)

    def test_negative_clauses(self):
        with self.assertRaises(ValueError):
            RandomKCNF(3,5,-1)
