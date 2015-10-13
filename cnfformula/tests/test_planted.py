from cnfformula.cnf import CNF
from cnfformula import RandomKCNF

from . import TestCNFBase

class TestPlanted(TestCNFBase) :
    def test_not_planted(self) :
        F = RandomKCNF(4,10,20,42)
        G = RandomKCNF(4,10,20,42,[])
        self.assertCnfEqual(F,G)

    def test_one(self) :
        ass = [{'x_1': True, 'x_2': False}]
        F = RandomKCNF(2,2,3,planted_assignments=ass)
        G = CNF([
            [(True,'x_1'),(False,'x_2')],
            [(False,'x_1'),(False,'x_2')],
            [(True,'x_1'),(True,'x_2')],
        ])
        self.assertCnfEqual(F,G)

    def test_most(self) :
        ass = [
            {'x_1': True, 'x_2': False},
            {'x_1': False, 'x_2': False},
            {'x_1': True, 'x_2': True},
        ]
        F = RandomKCNF(2,2,1,planted_assignments=ass)
        G = CNF([[(True,'x_1'),(False,'x_2')]])
        self.assertCnfEqual(F,G)

    def test_all(self):
        ass = [
            {'x_1': False, 'x_2': True},
            {'x_1': True, 'x_2': False},
            {'x_1': False, 'x_2': False},
            {'x_1': True, 'x_2': True},
        ]
        with self.assertRaises(ValueError):
            RandomKCNF(2,2,1,planted_assignments=ass)
