import networkx as nx
from cnfgen import CNF
from cnfgen import DominatingSet
from cnfgen.clitools import cnfgen, CLIError
from cnfgen.graphs import Graph

import pytest
from tests.utils import assertCnfEqual, assertCnfEqualsIgnoreVariables


def test_novertices():
    G = CNF()
    graph = nx.Graph()
    F = DominatingSet(graph, 1)
    assertCnfEqual(F, G)


def test_bad_arg():
    graph = nx.Graph()
    with pytest.raises(ValueError):
        DominatingSet(graph, 0)


def test_cycles():
    for n in range(10, 15):
        graph = nx.cycle_graph(n)
        F = DominatingSet(graph, (n+2)//3)
        assert F.is_satisfiable()
        F = DominatingSet(graph, (n+2)//3-1)
        assert not F.is_satisfiable()



def test_complete():
    for n in range(10, 12):
        parameters = ["cnfgen", "-q", "domset", 1, "complete", n]
        F = cnfgen(parameters, mode='formula')
        assert F.is_satisfiable()


def test_empty():
    for n in range(10, 12):
        parameters = ["cnfgen", "-q", "domset",n-1, "empty", n]
        F = cnfgen(parameters, mode='formula')
        assert not F.is_satisfiable()
