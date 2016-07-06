import networkx as nx
import sys

from cnfformula import CNF
from cnfformula import PerfectMatchingPrinciple, GraphPigeonholePrinciple, TseitinFormula
from cnfformula.cmdline import bipartite_random_graph

from . import TestCNFBase
from .test_commandline_helper import TestCommandline
from .test_graph_helper import complete_bipartite_graph_proper


class TestPerfectMatching(TestCNFBase):
    def test_empty(self):
        G = CNF()
        graph = nx.Graph()
        F = PerfectMatchingPrinciple(graph)
        self.assertCnfEqual(F,G)

    def test_complete_bipartite(self):
        graph = complete_bipartite_graph_proper(5,7)
        G = GraphPigeonholePrinciple(graph, functional=True, onto=True)
        F = PerfectMatchingPrinciple(graph)
        self.assertCnfEquivalentModuloVariables(F,G)

    def test_random_bipartite(self):
        graph = bipartite_random_graph(5,7,.3, seed=42)
        G = GraphPigeonholePrinciple(graph, functional=True, onto=True)
        F = PerfectMatchingPrinciple(graph)
        self.assertCnfEquivalentModuloVariables(F,G)

    def test_cycle(self):
        for n in range(3,8):
            graph = nx.cycle_graph(n)
            F = PerfectMatchingPrinciple(graph)
            G = TseitinFormula(graph,[1]*n)
            self.assertCnfEquivalentModuloVariables(F,G)

class TestPerfectMatchingCommandline(TestCommandline):
    def test_complete(self):
        for n in range(2,5):
            parameters = ["cnfgen", "matching", "--complete", n]
            graph = nx.complete_graph(n)
            F = PerfectMatchingPrinciple(graph)
            self.checkFormula(sys.stdin,F, parameters)
