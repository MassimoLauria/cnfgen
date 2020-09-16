import pytest
import networkx as nx
from networkx.algorithms.bipartite import complete_bipartite_graph

from cnfgen import CNF
from cnfgen import SubsetCardinalityFormula

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs


def test_empty():
    G = CNF()
    graph = nx.Graph()
    F = SubsetCardinalityFormula(graph)
    assertCnfEqual(F, G)


def test_not_bipartite():
    graph = nx.complete_graph(3)
    with pytest.raises(ValueError):
        SubsetCardinalityFormula(graph)


def test_complete_even():
    graph = complete_bipartite_graph(2, 2)
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
    graph = complete_bipartite_graph(2, 3)
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
    graph = complete_bipartite_graph(3, 3)
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


def test_cli_complete():
    for rows in range(2, 5):
        for columns in range(2, 5):
            parameters = [
                "cnfgen", "-q", "subsetcard", "complete",
                str(rows),
                str(columns)
            ]
            graph = complete_bipartite_graph(rows, columns)
            F = SubsetCardinalityFormula(graph)

            lib = F.dimacs(export_header=False)
            cli = cnfgen(parameters, mode='string')
            assert cli == lib


def test_cli_not_bipartite():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "subsetcard", "gnd", "10", "5", "3"])


def test_cli_shortcut_one_arg():
    F = cnfgen(["cnfgen", "-q", "subsetcard", "10"], mode='formula')
    # 10 x 10 4 regular graph + 1 edge: 41 vars
    assert len(F.variables()) == 41


def test_cli_shortcut_two_args():
    F = cnfgen(["cnfgen", "-q", "subsetcard", "15" "6"])
    # 10 x 10 6-regular graph + 1 edge: 61 vars
    assert len(F.variables()) == 61
