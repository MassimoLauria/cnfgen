import networkx as nx

import sys
from cnfformula import CNF
from cnfformula import SubsetCardinalityFormula

from . import TestCNFBase
from .test_commandline_helper import TestCommandline
from .test_graph_helper import complete_bipartite_graph_proper


class TestSubsetCardinality(TestCNFBase):
    def test_empty(self):
        G = CNF()
        graph = nx.Graph()
        F = SubsetCardinalityFormula(graph)
        self.assertCnfEqual(F,G)

    def test_not_bipartite(self):
        graph = nx.complete_graph(3)
        with self.assertRaises(KeyError):
            SubsetCardinalityFormula(graph)

    def test_complete_even(self):
        graph = complete_bipartite_graph_proper(2,2)
        F = SubsetCardinalityFormula(graph)
        dimacs = """\
        p cnf 4 4
        1 2 0
        3 4 0
        -1 -3 0
        -2 -4 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_complete_even_odd(self):
        graph = complete_bipartite_graph_proper(2,3)
        F = SubsetCardinalityFormula(graph)
        dimacs = """\
        p cnf 6 9
        1 2 0
        1 3 0
        2 3 0
        4 5 0
        4 6 0
        5 6 0
        -1 -4 0
        -2 -5 0
        -3 -6 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_complete_odd(self):
        graph = complete_bipartite_graph_proper(3,3)
        F = SubsetCardinalityFormula(graph)
        dimacs = """\
        p cnf 9 18
        1 2 0
        1 3 0
        2 3 0
        4 5 0
        4 6 0
        5 6 0
        7 8 0
        7 9 0
        8 9 0
        -1 -4 0
        -1 -7 0
        -4 -7 0
        -2 -5 0
        -2 -8 0
        -5 -8 0
        -3 -6 0
        -3 -9 0
        -6 -9 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)        
        
class TestSubsetCardinalityCommandline(TestCommandline):
    def test_complete(self):
        for rows in range(2,5):
            for columns in range(2,5):
                parameters = ["cnfgen","subsetcard", "--bcomplete", rows, columns]
                graph = complete_bipartite_graph_proper(rows, columns)
                F = SubsetCardinalityFormula(graph)
                self.checkFormula(sys.stdin,F, parameters)

    def test_not_bipartite(self):
        parameters = ["cnfgen","subsetcard", "--complete", "3"]
        self.checkCrash(sys.stdin, parameters)
