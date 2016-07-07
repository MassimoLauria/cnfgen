from cnfformula import CNF,PebblingFormula
import sys
from . import TestCNFBase
from test_commandline_helper import TestCommandline

import networkx as nx

class TestPebbling(TestCNFBase) :
    def test_null_graph(self) :
        G=nx.DiGraph()
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertCnfEqual(peb,CNF())

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

class TestPebblingCommandline(TestCommandline):
    def test_tree(self):
        for sz in range(1,5):
            G = nx.balanced_tree(2,sz,nx.DiGraph()).reverse()
            G = nx.relabel_nodes(G,dict(zip(G.nodes(),reversed(G.nodes()))),True)
            G.name = 'Complete binary tree of height {}'.format(sz)
            F = PebblingFormula(G)
            self.checkFormula(sys.stdin,F, ["cnfgen","peb", "--tree", sz])

    def test_pyramid(self):
        G = nx.DiGraph()
        G.add_edges_from([(1,4),(2,4),(2,5),(3,5),(4,6),(5,6)])
        G.name = 'Pyramid of height 2'
        F = PebblingFormula(G)
        self.checkFormula(sys.stdin,F, ["cnfgen","peb", "--pyramid", 2])
