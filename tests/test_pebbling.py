from cnfformula import CNF,PebblingFormula
import sys
from . import TestCNFBase
from .test_commandline_helper import TestCommandline

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
        F = CNF()
        F.add_variable('x')
        F.add_clause([(True,'x')])
        F.add_clause([(False,'x')])
        self.assertCnfEqual(F,peb)

    def test_path(self) :
        G = nx.path_graph(10,nx.DiGraph())
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        F = CNF()
        for i in range(10):
            F.add_variable(i)
        F.add_clause([(True,0)])
        for i in range(1,10):
            F.add_clause([(False,i-1),(True,i)])
        F.add_clause([(False,9)])
        self.assertCnfEqual(F,peb)

    def test_star(self) :
        G=nx.DiGraph()
        G.add_node(10)
        for i in range(0,10) :
            G.add_node(i)
            G.add_edge(i,10)
        peb = PebblingFormula(G)
        self.assertTrue(peb._check_coherence())

        F = CNF()
        for i in range(10):
            F.add_variable(i)
        for i in range(10):
            F.add_clause([(True,i)])
        F.add_clause( [(False,i) for i in range(10)] + [(True,10)] )
        F.add_clause([(False,10)])
        self.assertCnfEqual(F,peb)
        
    def test_cycle(self) :
        G=nx.cycle_graph(10,nx.DiGraph())
        with self.assertRaises(ValueError,msg='Pebbling formula created on graph with cycles') :
            PebblingFormula(G)

class TestPebblingCommandline(TestCommandline):
    def test_tree(self):
        for sz in range(1,5):
            G = nx.balanced_tree(2,sz,nx.DiGraph()).reverse()
            G = nx.relabel_nodes(G,dict(list(zip(G.nodes(),reversed(list(G.nodes()))))),True)
            G.name = 'Complete binary tree of height {}'.format(sz)
            F = PebblingFormula(G)
            self.checkFormula(sys.stdin,F, ["cnfgen","-q","peb", "--tree", sz])

    def test_pyramid(self):
        G = nx.DiGraph()
        G.add_edges_from([(1,4),(2,4),(2,5),(3,5),(4,6),(5,6)])
        G.name = 'Pyramid of height 2'
        F = PebblingFormula(G)
        self.checkFormula(sys.stdin,F, ["cnfgen","-q","peb", "--pyramid", 2])
