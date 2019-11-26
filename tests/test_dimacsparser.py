
from cnfformula import CNF
from cnfformula import RandomKCNF

from cnfformula.utils import dimacs2cnf

from .test_cnfformula import TestCNF

import io

class TestDimacsParser(TestCNF) :
    def test_empty_file(self) :
        dimacs = io.StringIO()
        with self.assertRaises(ValueError) :
            dimacs2cnf(dimacs)

    def test_empty_cnf(self) :
        dimacs = io.StringIO("p cnf 0 0\n")
        cnf = dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf, CNF())

    def test_comment_only_file(self) :
        dimacs = io.StringIO("c Hej!\n")
        with self.assertRaises(ValueError) :
            dimacs2cnf(dimacs)

    def test_invalid_file(self) :
        dimacs = io.StringIO("Hej!\n")
        with self.assertRaises(ValueError) :
            dimacs2cnf(dimacs)

    def test_commented_empty_cnf(self) :
        dimacs = io.StringIO("c Hej!\np cnf 0 0\n")
        cnf = dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf, CNF())

    def test_one_clause_cnf(self) :
        dimacs = io.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
        cnf = dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf, CNF([[(True, 1),(False, 2)]]))

    def test_one_var_cnf(self) :
        dimacs = io.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
        cnf = dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf, CNF([[(True, 1)],[(False, 1)]]))
    
    def test_double_conversion(self) :
        cnf = CNF()
        cnf.add_variable(1)
        cnf.add_variable(2)
        cnf.add_clause([(True,2),(False,1)])
        dimacs = io.StringIO(cnf.dimacs())
        cnf2 = dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf2,cnf)

    def test_double_conversion_random(self) :
        cnf = RandomKCNF(4,10,100)
        dimacs = io.StringIO(cnf.dimacs())
        cnf2 = dimacs2cnf(dimacs)
        self.assertCnfEquivalentModuloVariables(cnf,cnf2)
