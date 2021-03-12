import networkx as nx

import pytest

from cnfgen import CNF
from cnfgen import PerfectMatchingPrinciple
from cnfgen import GraphPigeonholePrinciple
from cnfgen import TseitinFormula

from networkx.algorithms.bipartite import random_graph as bipartite_random_graph
from networkx.algorithms.bipartite import complete_bipartite_graph
from cnfgen.graphs import Graph, BipartiteGraph, CompleteBipartiteGraph

from cnfgen.clitools import cnfgen
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = Graph(0)
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqual(F, G)


def test_complete_bipartite():
    G = complete_bipartite_graph(5, 7)
    B = CompleteBipartiteGraph(5, 7)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(G)
    assertCnfEqualsIgnoreVariables(PHP, PM)


def test_random_bipartite():
    G = bipartite_random_graph(5, 7, .3, seed=42)
    B = BipartiteGraph.from_networkx(G)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(G)
    assertCnfEqualsIgnoreVariables(PHP, PM)


@pytest.mark.parametrize('n', range(3, 8))
def test_cycle(n):
    graph = nx.cycle_graph(n)
    F = PerfectMatchingPrinciple(graph)
    G = TseitinFormula(graph, [1] * n)
    assertCnfEqualsIgnoreVariables(F, G)


@pytest.mark.parametrize('n', range(2, 5))
def test_complete(n):
    parameters = ["cnfgen", "-q", "matching", "complete", n]
    G = Graph.complete_graph(n)
    F = PerfectMatchingPrinciple(G)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli
