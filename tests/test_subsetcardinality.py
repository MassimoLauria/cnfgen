import pytest
import networkx as nx
from itertools import product

from cnfgen import CNF
from cnfgen import SubsetCardinalityFormula
from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs


def test_empty():
    G = CNF()
    graph = BipartiteGraph(0, 0)
    F = SubsetCardinalityFormula(graph)
    assertCnfEqual(F, G)


def test_not_bipartite():
    graph = nx.complete_graph(3)
    with pytest.raises(ValueError):
        SubsetCardinalityFormula(graph)


def test_complete_even():
    graph = CompleteBipartiteGraph(2, 2)
    F = SubsetCardinalityFormula(graph)
    dimacs = """\
    p cnf 4 4
    1 2 0
    3 4 0
    -1 -3 0
    -2 -4 0
    """
    assertCnfEqualsDimacs(F, dimacs)


def test_complete_even_odd():
    graph = CompleteBipartiteGraph(2, 3)
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
    assertCnfEqualsDimacs(F, dimacs)


def test_complete_odd():
    graph = CompleteBipartiteGraph(3, 3)
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
    assertCnfEqualsDimacs(F, dimacs)


cli_complete_cases=product(range(2, 5),range(2, 5))

@pytest.mark.parametrize('rows,columns', cli_complete_cases)
def test_cli_complete(rows,columns):
    parameters = [
        "cnfgen", "-q", "subsetcard", "complete",
        rows,
        columns
    ]
    graph = CompleteBipartiteGraph(rows, columns)
    F = SubsetCardinalityFormula(graph)

    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert cli == lib


def test_cli_not_bipartite():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "subsetcard", "gnd", "10", "5", "3"])


def test_cli_shortcut_one_arg():
    F = cnfgen(["cnfgen", "-q", "subsetcard", "10"], mode='formula')
    # 10 x 10 4 regular graph + 1 edge: 41 vars
    assert F.number_of_variables() == 41


def test_cli_shortcut_two_args():
    F = cnfgen(["cnfgen", "-q", "subsetcard", "15", "6"], mode='formula')
    # 15 x 15 6-regular graph + 1 edge: 91 vars
    assert F.number_of_variables() == 91
