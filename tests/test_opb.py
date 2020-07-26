from cnfformula.cnf import CNF

from . import TestCNFBase

import random
import itertools

class TestOPB(TestCNFBase) :

    def test_empty(self) :
        opb="""\
        * #variable= 0 #constraint= 0
        *
        """
        F=CNF()
        self.assertCnfEqualsOPB(F,opb)

    def test_one_clause(self) :
        opb="""\
        * #variable= 4 #constraint= 1
        *
        +1 x1 +1 x2 -1 x3 -1 x4 >= -1;
        """
        F=CNF()
        F.add_clause([(True,"a"),(True,"b"),(False,"c"),(False,"d")])
        self.assertCnfEqualsOPB(F,opb)

    def test_one_geq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +1 x2 +1 x3 +1 x4 +1 x5 >= 2;
        """
        F=CNF()
        F.add_greater_or_equal(["a","b","c","d","e"],2)
        self.assertCnfEqualsOPB(F,opb)
    
    def test_one_gt(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +1 x2 +1 x3 +1 x4 +1 x5 >= 3;
        """
        F=CNF()
        F.add_strictly_greater_than(["a","b","c","d","e"],2)
        self.assertCnfEqualsOPB(F,opb)
    
    def test_one_leq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        -1 x1 -1 x2 -1 x3 -1 x4 -1 x5 >= -2;
        """
        F=CNF()
        F.add_less_or_equal(["a","b","c","d","e"],2)
        self.assertCnfEqualsOPB(F,opb)
    
    def test_one_lt(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        -1 x1 -1 x2 -1 x3 -1 x4 -1 x5 >= -1;
        """
        F=CNF()
        F.add_strictly_less_than(["a","b","c","d","e"],2)
        self.assertCnfEqualsOPB(F,opb)
    
    def test_one_eq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +1 x2 +1 x3 +1 x4 +1 x5 = 2;
        """
        F=CNF()
        F.add_equal_to(["a","b","c","d","e"],2)
        self.assertCnfEqualsOPB(F,opb)

    def test_weighted_geq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +2 x2 +3 x3 -1 x4 -2 x5 >= 2;
        """
        F=CNF()
        F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e",">=",2)
        self.assertCnfEqualsOPB(F,opb)

    def test_weighted_gt(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +2 x2 +3 x3 -1 x4 -2 x5 >= 3;
        """
        F=CNF()
        F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e",">",2)
        self.assertCnfEqualsOPB(F,opb)

    def test_weighted_leq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        -1 x1 -2 x2 -3 x3 +1 x4 +2 x5 >= -2;
        """
        F=CNF()
        F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e","<=",2)
        self.assertCnfEqualsOPB(F,opb)

    def test_weighted_lt(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        -1 x1 -2 x2 -3 x3 +1 x4 +2 x5 >= -1;
        """
        F=CNF()
        F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e","<",2)
        self.assertCnfEqualsOPB(F,opb)

    def test_weighted_eq(self) :
        opb="""\
        * #variable= 5 #constraint= 1
        *
        +1 x1 +2 x2 +3 x3 -1 x4 -2 x5 = 2;
        """
        F=CNF()
        F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e","==",2)
        self.assertCnfEqualsOPB(F,opb)

    def test_bogus(self) :
        F=CNF()
        with self.assertRaises(ValueError):
            F.add_linear(1,"a",2,"b",3,"c",-1,"d",-2,"e","??",2)

    def test_parity(self) :
        opb="""\
        * #variable= 3 #constraint= 4
        *
        +1 x1 +1 x2 +1 x3 >= 1;
        +1 x1 -1 x2 -1 x3 >= -1;
        -1 x1 +1 x2 -1 x3 >= -1;
        -1 x1 -1 x2 +1 x3 >= -1;
        """
        F=CNF()
        F.add_parity(["a","b","c"],1)
        self.assertCnfEqualsOPB(F,opb)
