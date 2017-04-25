from cnfformula import CNF, Expand

from . import TestCNFBase

class TestExpand(TestCNFBase) :

    def test_empty(self) :
        cnf=CNF()
        lift=Expand(cnf)
        self.assertCnfEqual(cnf,lift)

    def test_one_clause(self) :
        dimacs="""\
        p cnf 4 1
        1 2 -3 -4 0
        """
        opb="""\
        * #variable= 4 #constraint= 1
        *
        +1 x1 +1 x2 -1 x3 -1 x4 >= -1;
        """
        F=CNF()
        F.add_clause([(True,"a"),(True,"b"),(False,"c"),(False,"d")])
        F = Expand(F)
        self.assertCnfEqualsDimacs(F,dimacs)
        self.assertCnfEqualsOPB(F,opb)

    def test_one_inequality(self) :
        dimacs="""\
        p cnf 3 3
        1 2 0
        1 3 0
        2 3 0
        """
        opb="""\
        * #variable= 3 #constraint= 3
        *
        +1 x1 +1 x2 >= 1;
        +1 x1 +1 x3 >= 1;
        +1 x2 +1 x3 >= 1;
        """
        F=CNF()
        F.add_greater_or_equal(["a","b","c"],2)
        F = Expand(F)
        self.assertCnfEqualsDimacs(F,dimacs)
        self.assertCnfEqualsOPB(F,opb)

    def test_contradiction(self) :
        dimacs="""\
        p cnf 3 1
        0
        """
        opb="""\
        * #variable= 3 #constraint= 1
        *
         >= 1;
        """
        F=CNF()
        F.add_greater_or_equal(["a","b","c"],4)
        F = Expand(F)
        self.assertCnfEqualsDimacs(F,dimacs)
        self.assertCnfEqualsOPB(F,opb)

    def test_subset_sum(self) :
        dimacs="""\
        p cnf 3 7
        -1 -2 -3 0
        -1 2 -3 0
        -1 2 3 0
        1 -2 -3 0
        1 -2 3 0
        1 2 -3 0
        1 2 3 0
        """
        F=CNF()
        F.add_linear(3,"a",5,"b",7,"c","==",8)
        F = Expand(F)
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_subset_sum_2(self) :
        dimacs="""\
        p cnf 3 8
        -1 -2 -3 0
        -1 -2 3 0
        -1 2 -3 0
        -1 2 3 0
        1 -2 -3 0
        1 -2 3 0
        1 2 -3 0
        1 2 3 0
        """
        F=CNF()
        F.add_linear(3,"a",5,"b",7,"c","==",6)
        F = Expand(F)
        self.assertCnfEqualsDimacs(F,dimacs)
