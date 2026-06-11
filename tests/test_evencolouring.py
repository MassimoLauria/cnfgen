from cnfgen import CNF
from cnfgen import EvenColoringFormula, TseitinFormula
from cnfgen.clitools import cnfgen, CLIError
from cnfgen.graphs import Graph, undirected_path_graph,undirected_cycle_graph

import pytest
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = Graph(0)
    F = EvenColoringFormula(graph)
    assertCnfEqual(F, G)


def test_odd_degree():
    graph = undirected_path_graph(2)
    with pytest.raises(ValueError):
        EvenColoringFormula(graph)


def test_cycle():
    for n in range(3, 8):
        graph = undirected_cycle_graph(n)
        F = EvenColoringFormula(graph)
        G = TseitinFormula(graph, [1] * n)
        assertCnfEqualsIgnoreVariables(F, G)


def test_even_degree_complete():
    for n in range(3, 8, 2):
        parameters = ["cnfgen", "-q", "ec", "complete", n]
        graph = Graph.complete_graph(n)
        F = EvenColoringFormula(graph)
        lib = F.to_dimacs()
        cli = cnfgen(parameters, mode='string')
        assert cli == lib


def test_odd_degree_complete():
    for n in range(4, 7, 2):
        parameters = ["cnfgen", "-q", "ec", "complete", n]
        with pytest.raises(CLIError):
            cnfgen(parameters)
