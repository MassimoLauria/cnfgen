#!/usr/bin/env python

from cnfformula import CNF
from cnfformula import GraphAutomorphism,GraphIsomorphism

from . import TestCNFBase

import unittest
import networkx as nx
import StringIO


class TestGraphIsomorphism(TestCNFBase):
    """Some basic test for the graph isomorphism formula."""

    def test_empty_vs_non_empty(self):
        """Empty graph is not isomorphic to a non empty graph."""
        G1=nx.Graph()
        G2=nx.complete_graph(3)
        cnf1 = CNF([[]]) # one empty clause
        cnf2 = GraphIsomorphism(G1,G2)
        self.assertCnfEqual(cnf1,cnf2)

    def test_empty_vs_empty(self):
        """Empty graphs are isomorphic."""
        G1=nx.Graph()
        G2=nx.Graph()
        cnf1 = CNF()
        cnf2 = GraphIsomorphism(G1,G2)
        self.assertCnfEqual(cnf1,cnf2)


class TestGraphAutomorphism(TestCNFBase):

    def test_empty_graph(self):
        """Empty graph has no nontrivial automorphism."""
        G1=nx.Graph()
        cnf1 = CNF([[]]) # one empty clause
        cnf2 = GraphAutomorphism(G1)
        self.assertCnfEqual(cnf1,cnf2)

    def test_single_vertex_graph(self):
        """Singleton graph has no nontrivial automorphism."""
        G1=nx.Graph()
        G1.add_node(0)
        cnf1 = GraphAutomorphism(G1)
        v = list(cnf1.variables())[0]
        cnf2 = CNF()
        cnf2.add_clause([(True,v)])
        cnf2.add_clause([(False,v)])
        self.assertCnfEqual(cnf1,cnf2)

    def test_example_graph_noauto(self):
        """Simple graph with no automorphisms."""
        G = nx.Graph()
        G.add_edges_from([(1, 2), (1, 3),
                          (2, 3), (2, 5),
                          (3, 4), (4, 5),
                          (4, 6)])
        F = GraphAutomorphism(G)
        self.assertUNSAT(F)

    def test_example_graph_auto(self):
        """Simple graph with automorphisms."""
        G = nx.cycle_graph(10)
        F = GraphAutomorphism(G)
        self.assertSAT(F)
