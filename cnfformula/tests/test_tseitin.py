from cnfformula import TseitinFormula

from . import TestCNFBase

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
