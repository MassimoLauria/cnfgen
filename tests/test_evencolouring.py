import networkx as nx
import sys

from cnfformula import CNF
from cnfformula import EvenColoringFormula, TseitinFormula

from . import TestCNFBase
from .test_commandline_helper import TestCommandline

class TestEvenColouring(TestCNFBase):
    def test_empty(self):
        G = CNF()
        graph = nx.Graph()
        F = EvenColoringFormula(graph)
        self.assertCnfEqual(F,G)

    def test_odd_degree(self):
        graph = nx.path_graph(2)
        with self.assertRaises(ValueError):
            EvenColoringFormula(graph)

    def test_cycle(self):
        for n in range(3,8):
            graph = nx.cycle_graph(n)
            F = EvenColoringFormula(graph)
            G = TseitinFormula(graph,[1]*n)
            self.assertCnfEquivalentModuloVariables(F,G)

class TestEvenColouringCommandline(TestCommandline):
    def test_complete(self):
        for n in range(3,8,2):
            parameters = ["cnfgen","ec", "--complete", n]
            graph = nx.complete_graph(n)
            F = EvenColoringFormula(graph)
            self.checkFormula(sys.stdin,F, parameters)

    def test_odd_degree(self):
        for n in range(4,7,2):
            parameters = ["cnfgen","ec", "--complete", n]
            self.checkCrash(sys.stdin,parameters)
