import networkx as nx
from cnfgen import CNF
from cnfgen import EvenColoringFormula, TseitinFormula
from cnfgen.clitools import cnfgen, CLIError

import pytest
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_empty():
    G = CNF()
    graph = nx.Graph()
    F = EvenColoringFormula(graph)
    assertCnfEqual(F, G)


def test_odd_degree():
    graph = nx.path_graph(2)
    with pytest.raises(ValueError):
        EvenColoringFormula(graph)


def test_cycle():
    for n in range(3, 8):
        graph = nx.cycle_graph(n)
        F = EvenColoringFormula(graph)
        G = TseitinFormula(graph, [1] * n)
        assertCnfEqualsIgnoreVariables(F, G)


def test_even_degree_complete():
    for n in range(3, 8, 2):
        parameters = ["cnfgen", "-q", "ec", "complete", n]
        graph = nx.complete_graph(n)
        F = EvenColoringFormula(graph)
        lib = F.dimacs(export_header=False)
        cli = cnfgen(parameters, mode='string')
        assert cli == lib


def test_odd_degree_complete():
    for n in range(4, 7, 2):
        parameters = ["cnfgen", "-q", "ec", "complete", n]
        with pytest.raises(CLIError):
            cnfgen(parameters)
