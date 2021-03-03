import sys
import networkx as nx
import pytest
import io

from cnfgen import TseitinFormula
from cnfgen.clitools import cnfgen, CLIError
from cnfgen.clitools import redirect_stdin
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs


def test_null():
    dimacs = """\
    p cnf 0 0
    """
    graph = nx.null_graph()
    F = TseitinFormula(graph)
    assertCnfEqualsDimacs(F, dimacs)


def test_empty_graph():
    dimacs = """\
    p cnf 0 1
    0
    """
    graph = nx.empty_graph(10)
    F = TseitinFormula(graph)
    assertCnfEqualsDimacs(F, dimacs)


def test_one_edge():
    dimacs = """\
    p cnf 1 2
    1 0
    -1 0
    """
    graph = nx.path_graph(2)
    F = TseitinFormula(graph)
    assertCnfEqualsDimacs(F, dimacs)


@pytest.mark.skip("Multigraphs not supported yet")
def test_multi_edge():
    dimacs = """\
    p cnf 2 4
    1 -2 0
    -1 2 0
    1 2 0
    -1 -2 0
    """
    graph = nx.MultiGraph()
    graph.add_nodes_from((0, 1))
    graph.add_edges_from(((0, 1), (0, 1)))
    F = TseitinFormula(graph)
    assertCnfEqualsDimacs(F, dimacs)


def test_star():
    graph = nx.star_graph(10)
    F = TseitinFormula(graph)
    assert F.number_of_variables() == 10
    assert F.number_of_clauses() == 2**9 + 10
    assert len([C for C in F.clauses() if len(C) == 10]) == 2**9
    assert len([C for C in F.clauses() if len(C) == 1]) == 10
    for C in F.clauses():
        if len(C) == 1:
            assert C[0]<0


def test_charge_even():
    graph = nx.star_graph(10)
    F = TseitinFormula(graph, [0] * 11)
    for C in F.clauses():
        if len(C) == 1:
            assert C[0]<0


def test_charge_odd():
    graph = nx.star_graph(10)
    F = TseitinFormula(graph, [1] * 11)
    for C in F.clauses():
        if len(C) == 1:
            assert C[0]>0


def test_charge_first():
    graph = nx.star_graph(10)
    F = TseitinFormula(graph, [1])
    G = TseitinFormula(graph)
    assertCnfEqual(F, G)


def test_parameters():
    for sz in range(1, 5):
        parameters = ["cnfgen", "-q", "tseitin", "first", "complete", sz]
        graph = nx.complete_graph(sz)
        F = TseitinFormula(graph)
        lib = F.to_dimacs()
        cli = cnfgen(parameters, mode='string')
        assert lib == cli


def test_commandline1():
    parameters = ["cnfgen", "-q", "tseitin", "randomodd", "gnd", 10, 4]
    assert cnfgen(parameters, mode='string') is not None


def test_commandline2():
    parameters = ["cnfgen", "-q", "tseitin", 'randomeven', "gnm", 10, 20]
    assert cnfgen(parameters, mode='string') is not None


def test_no_graph_format():
    with pytest.raises(CLIError):
        with redirect_stdin(io.StringIO('')):
            cnfgen(['cnfgen', 'tseitin', "randomodd"])


def test_short_commandline1():
    parameters = ["cnfgen", "-q", "tseitin", 10, 4]
    assert cnfgen(parameters, mode='string') is not None


def test_short_commandline2():
    parameters = ["cnfgen", "-q", "tseitin", 20, 5]
    assert cnfgen(parameters, mode='string') is not None
