import networkx as nx

from cnfgen import CNF
from cnfgen import PerfectMatchingPrinciple
from cnfgen import GraphPigeonholePrinciple
from cnfgen import TseitinFormula

from networkx.algorithms.bipartite import random_graph as bipartite_random_graph
from networkx.algorithms.bipartite import complete_bipartite_graph
from cnfgen.graphs import Graph,BipartiteGraph

from cnfgen.clitools import cnfgen
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = Graph(0)
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqual(F, G)


def test_complete_bipartite():
    G = complete_bipartite_graph(5, 7)
    B = BipartiteGraph.from_networkx(G)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(G)
    assertCnfEqualsIgnoreVariables(PHP, PM)


def test_random_bipartite():
    G = bipartite_random_graph(5, 7, .3, seed=42)
    B = BipartiteGraph.from_networkx(G)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(G)
    assertCnfEqualsIgnoreVariables(PHP, PM)


def test_cycle():
    for n in range(3, 8):
        graph = nx.cycle_graph(n)
        F = PerfectMatchingPrinciple(graph)
        G = TseitinFormula(graph, [1] * n)
        assertCnfEqualsIgnoreVariables(F, G)


def test_complete():
    for n in range(2, 5):
        parameters = ["cnfgen", "-q", "matching", "complete", n]
        graph = nx.complete_graph(n)
        F = PerfectMatchingPrinciple(graph)
        lib = F.dimacs(export_header=False)
        cli = cnfgen(parameters, mode='string')
        assert lib == cli
