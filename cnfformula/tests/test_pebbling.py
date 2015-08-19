from cnfformula.families import PebblingFormula

from . import TestCNFBase

import cnfformula

import unittest
import networkx as nx

class TestPebbling(TestCNFBase) :
    def test_null_graph(self) :
        G=nx.DiGraph()
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertCnfEqual(peb,cnfformula.CNF())

    def test_single_vertex(self) :
        G=nx.DiGraph()
        G.add_node('x')
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertSetEqual(set(peb.variables()),set(['x']))
        self.assertSetSetEqual(list(peb.clauses()),[[(True,'x')],[(False,'x')]])

    def test_path(self) :
        G=nx.path_graph(10,nx.DiGraph())
        peb = PebblingFormula(G)
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
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        clauses = \
            [[(True,i)] for i in xrange(10)] + \
            [[(False,i) for i in xrange(10)] + [(True,10)]] + \
            [[(False,10)]]
        self.assertListEqual(list(peb.variables()),range(11))
        self.assertSetSetEqual(peb.clauses(),clauses)
        
    def test_cycle(self) :
        G=nx.cycle_graph(10,nx.DiGraph())
        with self.assertRaises(ValueError) :
            PebblingFormula(G)


if __name__ == '__main__':
    unittest.main()
