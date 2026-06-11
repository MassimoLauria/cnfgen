import pytest

from cnfgen import CNF
from cnfgen import PerfectMatchingPrinciple
from cnfgen import GraphPigeonholePrinciple
from cnfgen import TseitinFormula
from cnfgen import MutilatedChessboard

from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph,bipartite_random
from cnfgen.graphs import Graph, undirected_cycle_graph

from cnfgen.clitools import cnfgen
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = Graph(0)
    F = PerfectMatchingPrinciple(graph)
    assertCnfEqual(F, G)


def test_complete_bipartite():
    B = CompleteBipartiteGraph(5, 7)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(B)
    assertCnfEqualsIgnoreVariables(PHP, PM)


def test_random_bipartite():
    B = bipartite_random(5, 7, .3, seed=42)
    PHP = GraphPigeonholePrinciple(B, functional=True, onto=True)
    PM = PerfectMatchingPrinciple(B)
    assertCnfEqualsIgnoreVariables(PHP, PM)


@pytest.mark.parametrize('n', range(3, 8))
def test_cycle(n):
    graph = undirected_cycle_graph(n)
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


def test_mchess8x8():
    F = MutilatedChessboard(8,8)
    assert F.number_of_variables() == 7*8*2-4

def test_mchess2x2():
    F = MutilatedChessboard(2,2)
    assert F.number_of_variables() == 0
    assert not F.is_satisfiable()

def test_mchess4x4():
    F = MutilatedChessboard(4,4)
    assert F.number_of_variables() == 3*4*2-4
    assert not F.is_satisfiable()

def test_mchess3x3():
    F = MutilatedChessboard(3,3)
    assert F.number_of_variables() == 2*3*2-4
    assert not F.is_satisfiable()

def test_mchess3x4():
    F = MutilatedChessboard(3,4)
    assert F.number_of_variables() == 2*4 + 3*3 - 4
    assert F.is_satisfiable()

def test_mchess_bad_arg1():
    with pytest.raises(ValueError):
        MutilatedChessboard(1,3)

def test_mchess_bad_arg2():
    with pytest.raises(ValueError):
        MutilatedChessboard(1,3)

@pytest.mark.parametrize('w,h',[(w,h) for w in range(2, 5) for h in range(2,5) ])
def test_mchess_cli(w,h):
    parameters = ["cnfgen", "-q", "mchess", w, h]
    F = MutilatedChessboard(w,h)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli
    assert F.is_satisfiable() == ( (w+h)%2  == 1)
