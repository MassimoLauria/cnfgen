import cnfformula
import cnfformula.utils as cnfutils

from test_cnfformula import TestCNF

import StringIO

class TestDimacsParser(TestCNF) :
    def test_empty_file(self) :
        dimacs = StringIO.StringIO()
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_empty_cnf(self) :
        dimacs = StringIO.StringIO("p cnf 0 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF())

    def test_comment_only_file(self) :
        dimacs = StringIO.StringIO("c Hej!\n")
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_invalid_file(self) :
        dimacs = StringIO.StringIO("Hej!\n")
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_commented_empty_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 0 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF())

    def test_one_clause_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF([[(True, 1),(False, 2)]]))

    def test_one_var_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF([[(True, 1)],[(False, 1)]]))
    
    def test_inverse(self) :
        cnf = TestCNF.sorted_cnf([[(True,2),(False,1)]])
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf2,cnf)

    def test_inverse_random(self) :
        cnf = self.random_cnf(4,10,100)
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf2,cnf)
