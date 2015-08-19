import cnfformula

from . import TestCNFBase

class TestSubstitution(TestCNFBase) :
    def test_or(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,lift2)

    def test_xor(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,lift2)

    def test_majority(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'maj', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^2'),(False,'{y}^0')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2'),(False,'{y}^0')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^2'),(False,'{y}^0')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'maj', 3)
        self.assertCnfEqual(lift,lift2)
        
    def test_equality(self) :
        cnf = cnfformula.CNF([[(False,'x'),(True,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,lift2)

    def test_inequality(self) :
        cnf = cnfformula.CNF([[(False,'x'),(True,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'neq', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(True,'{y}^1')],
                    [(True,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                ]))

    def test_inequality_pos_clause(self) :
        cnf = cnfformula.CNF([[(True,'x')]])
        lift = cnfformula.TransformFormula(cnf, 'neq', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{x}^2')]
                ]))

    def test_eq_vs_neq(self) :
        cnf = cnfformula.CNF([
                [(False,'x'),(True,'y')],
                [(True,'z'),(True,'t')],
                [(False,'u'),(False,'v')]
                ])
        cnfneg = cnfformula.CNF([
                [(True,'x'),(False,'y')],
                [(False,'z'),(False,'t')],
                [(True,'u'),(True,'v')]
                ])
        lifteq = cnfformula.TransformFormula(cnf, 'eq', 4)
        liftneq = cnfformula.TransformFormula(cnfneg, 'neq', 4)
        self.assertCnfEqual(lifteq, liftneq)

    def test_if_then_else(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'ite')
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^2'),(True,'{y}^0'),(False,'{y}^2')],
        ]))
        lift2 = cnfformula.TransformFormula(cnf, 'ite', 42)
        self.assertCnfEqual(lift,lift2)

    def test_exactly_one(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'one', 2)

        lift2 = cnfformula.TransformFormula(cnf, 'one', 2)
        self.assertCnfEqual(lift,lift2)
