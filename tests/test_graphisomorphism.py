#!/usr/bin/env python

import pytest
import networkx as nx

from cnfformula import CNF
from cnfformula import GraphAutomorphism, GraphIsomorphism

from tests.utils import assertSAT, assertUNSAT, assertCnfEqual


def test_empty_vs_non_empty():
    """Empty graph is not isomorphic to a non empty graph."""
    G1 = nx.Graph()
    G2 = nx.complete_graph(3)
    cnf1 = CNF([[]])  # one empty clause
    cnf2 = GraphIsomorphism(G1, G2)
    assertCnfEqual(cnf1, cnf2)


def test_empty_vs_empty():
    """Empty graphs are isomorphic."""
    G1 = nx.Graph()
    G2 = nx.Graph()
    cnf1 = CNF()
    cnf2 = GraphIsomorphism(G1, G2)
    assertCnfEqual(cnf1, cnf2)


def test_empty_graph():
    """Empty graph has no nontrivial automorphism."""
    G1 = nx.Graph()
    cnf1 = CNF([[]])  # one empty clause
    cnf2 = GraphAutomorphism(G1)
    assertCnfEqual(cnf1, cnf2)


def test_single_vertex_graph():
    """Singleton graph has no nontrivial automorphism."""
    G1 = nx.Graph()
    G1.add_node(0)
    cnf1 = GraphAutomorphism(G1)
    v = list(cnf1.variables())[0]
    cnf2 = CNF()
    cnf2.add_clause([(True, v)])
    cnf2.add_clause([(False, v)])
    assertCnfEqual(cnf1, cnf2)


def test_example_graph_noauto():
    """Simple graph with no automorphisms."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 5), (3, 4), (4, 5), (4, 6)])
    F = GraphAutomorphism(G)
    assertUNSAT(F)


def test_example_graph_auto():
    """Simple graph with automorphisms."""
    G = nx.cycle_graph(10)
    F = GraphAutomorphism(G)
    assertSAT(F)
