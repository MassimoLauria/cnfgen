import cnfgen
import reshuffle

import unittest
import networkx as nx
import StringIO
import random

class TestCNF(unittest.TestCase) :
    def assertCnfEqual(self,cnf1,cnf2) :
        self.assertSetEqual(set(cnf1.variables()),set(cnf2.variables()))
        self.assertSetSetEqual(cnf1.clauses(),cnf2.clauses())

    def assertSetSetEqual(self,list1,list2) :
        set1=set(frozenset(x) for x in list1)
        set2=set(frozenset(x) for x in list2)
        self.assertSetEqual(set1,set2)

    @staticmethod
    def randomCnf(width, num_variables, num_clauses) :
        return cnfgen.CNF([
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
    def test_empty(self) :
        F=cnfgen.CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

class TestPebbling(TestCNF) :
    def test_null_graph(self) :
        G=nx.DiGraph()
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertCnfEqual(peb,cnfgen.CNF())

    def test_single_vertex(self) :
        G=nx.DiGraph()
        G.add_node('x')
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertSetEqual(set(peb.variables()),set(['x']))
        self.assertSetSetEqual(list(peb.clauses()),[[(True,'x')],[(False,'x')]])

    def test_path(self) :
        G=nx.path_graph(10,nx.DiGraph())
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        clauses = \
            [[(True,0)]] + \
            [[(False,i-1),(True,i)] for i in xrange(1,10)] + \
            [[(False,9)]]
        self.assertListEqual(list(peb.variables()),range(10))
        self.assertSetSetEqual(peb.clauses(),clauses)

    def test_pyramid(self) :
        G=nx.DiGraph()
        G.add_node(10)
        for i in xrange(0,10) :
            G.add_node(i)
            G.add_edge(i,10)
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        clauses = \
            [[(True,i)] for i in xrange(10)] + \
            [[(False,i) for i in xrange(10)] + [(True,10)]] + \
            [[(False,10)]]
        self.assertListEqual(list(peb.variables()),range(11))
        self.assertSetSetEqual(peb.clauses(),clauses)
        
    def test_cycle(self) :
        G=nx.cycle_graph(10,nx.DiGraph())
        with self.assertRaises(RuntimeError) :
            peb = cnfgen.PebblingFormula(G)

class TestDimacsParser(TestCNF) :
    def test_empty_file(self) :
        dimacs = StringIO.StringIO()
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_empty_cnf(self) :
        dimacs = StringIO.StringIO("p cnf 0 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF())

    def test_comment_only_file(self) :
        dimacs = StringIO.StringIO("c Hej!\n")
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_invalid_file(self) :
        dimacs = StringIO.StringIO("Hej!\n")
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_commented_empty_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 0 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF())

    def test_one_clause_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF([[(True, 1),(False, 2)]]))

    def test_one_var_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF([[(True, 1)],[(False, 1)]]))
    
    def test_inverse(self) :
        cnf = self.randomCnf(4,10,100)
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf2,cnf)

if __name__ == '__main__':
    unittest.main()
