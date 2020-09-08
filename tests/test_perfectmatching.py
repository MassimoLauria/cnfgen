import networkx as nx

from cnfgen import CNF
from cnfgen import PerfectMatchingPrinciple
from cnfgen import GraphPigeonholePrinciple
from cnfgen import TseitinFormula

from networkx.algorithms.bipartite import random_graph as bipartite_random_graph
from networkx.algorithms.bipartite import complete_bipartite_graph

from cnfgen.clitools import cnfgen
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = nx.Graph()
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqual(F, G)


def test_complete_bipartite():
    graph = complete_bipartite_graph(5, 7)
    G = GraphPigeonholePrinciple(graph, functional=True, onto=True)
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqualsIgnoreVariables(F, G)


def test_random_bipartite():
    graph = bipartite_random_graph(5, 7, .3, seed=42)
    G = GraphPigeonholePrinciple(graph, functional=True, onto=True)
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqualsIgnoreVariables(F, G)


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
