from cnfformula import RandomKCNF

from . import TestCNFBase

class TestRandomCNF(TestCNFBase) :
    def test_empty_cnf(self) :
        F = RandomKCNF(0,0,0)
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

    def test_empty_cnf_with_vars(self) :
        F = RandomKCNF(0,10,0)
        self.assertListEqual(list(F.variables()),range(1,11))
        self.assertListEqual(list(F.clauses()),[])

    def test_random_cnf(self) :
        F = RandomKCNF(3,10,50)
        self.assertListEqual(list(F.variables()),range(1,11))
        self.assertEqual(len(F),50)
        self.assertEqual(len(set(frozenset(x) for x in F.clauses())),50)
