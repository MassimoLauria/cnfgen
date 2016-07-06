from cnfformula import TseitinFormula

from . import TestCNFBase
from test_commandline_helper import TestCommandline

import sys
import unittest
import networkx as nx

class TestTseitin(TestCNFBase):
    def test_null(self):
        dimacs = """\
        p cnf 0 0
        """
        graph=nx.null_graph()
        F = TseitinFormula(graph)
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_empty_graph(self):
        dimacs = """\
        p cnf 0 1
        0
        """
        graph=nx.empty_graph(10)
        F = TseitinFormula(graph)
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_edge(self):
        dimacs = """\
        p cnf 1 2
        1 0
        -1 0
        """
        graph=nx.path_graph(2)
        F = TseitinFormula(graph)
        self.assertCnfEqualsDimacs(F,dimacs)

    @unittest.skip("Multigraphs not supported yet")
    def test_multi_edge(self):
        dimacs = """\
        p cnf 2 4
        1 -2 0
        -1 2 0
        1 2 0
        -1 -2 0
        """
        graph=nx.MultiGraph()
        graph.add_nodes_from((0,1))
        graph.add_edges_from(((0,1),(0,1)))
        F = TseitinFormula(graph)
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_star(self):
        graph=nx.star_graph(10)
        F = TseitinFormula(graph)
        self.assertEquals(len(list(F.variables())),10)
        self.assertEquals(len(list(F.clauses())),2**9+10)
        self.assertEquals(len([C for C in F.clauses() if len(C)==10]),2**9)
        self.assertEquals(len([C for C in F.clauses() if len(C)==1]),10)
        for C in F.clauses():
            if len(C)==1:
                self.assertFalse(C[0][0])

    def test_charge_even(self):
        graph=nx.star_graph(10)
        F = TseitinFormula(graph,[0]*11)
        for C in F.clauses():
            if len(C)==1:
                self.assertFalse(C[0][0])

    def test_charge_odd(self):
        graph=nx.star_graph(10)
        F = TseitinFormula(graph,[1]*11)
        for C in F.clauses():
            if len(C)==1:
                self.assertTrue(C[0][0])

    def test_charge_first(self):
        graph=nx.star_graph(10)
        F = TseitinFormula(graph,[1])
        G = TseitinFormula(graph)
        self.assertCnfEqual(F,G)

class TestTseitinCommandline(TestCommandline):
    def test_parameters(self):
        for sz in range(1,5):
            parameters = ["cnfgen","tseitin", "--complete", sz]
            graph=nx.complete_graph(sz)
            F = TseitinFormula(graph)
            self.checkFormula(sys.stdin,F, parameters)
