import networkx as nx
import pytest
from cnfformula import CNF, PebblingFormula

from cnfgen.clitools import cnfgen
from tests.utils import assertCnfEqual


def test_null_graph():
    G = nx.DiGraph()
    peb = PebblingFormula(G)
    assert peb.debug()
    assertCnfEqual(peb, CNF())


def test_single_vertex():
    G = nx.DiGraph()
    G.add_node('x')
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    F.add_variable('x')
    F.add_clause([(True, 'x')])
    F.add_clause([(False, 'x')])
    assertCnfEqual(F, peb)


def test_path():

    G = nx.path_graph(10, nx.DiGraph())
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    for i in range(10):
        F.add_variable(i)
    F.add_clause([(True, 0)])
    for i in range(1, 10):
        F.add_clause([(False, i - 1), (True, i)])
    F.add_clause([(False, 9)])

    assertCnfEqual(F, peb)


def test_star():
    G = nx.DiGraph()
    G.add_node(10)
    for i in range(0, 10):
        G.add_node(i)
        G.add_edge(i, 10)
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    for i in range(10):
        F.add_variable(i)
    for i in range(10):
        F.add_clause([(True, i)])
    F.add_clause([(False, i) for i in range(10)] + [(True, 10)])
    F.add_clause([(False, 10)])
    assertCnfEqual(F, peb)


def test_cycle():
    G = nx.cycle_graph(10, nx.DiGraph())
    with pytest.raises(ValueError):
        PebblingFormula(G)


def test_tree():
    for sz in range(1, 5):
        G = nx.balanced_tree(2, sz, nx.DiGraph()).reverse()
        G = nx.relabel_nodes(
            G, dict(list(zip(G.nodes(), reversed(list(G.nodes()))))), True)
        G.name = 'Complete binary tree of height {}'.format(sz)

        F = PebblingFormula(G)
        lib = F.dimacs(export_header=False)
        cli = cnfgen(["cnfgen", "-q", "peb", "--tree", sz], mode='string')
        assert lib == cli


def test_pyramid():
    G = nx.DiGraph()
    G.add_edges_from([(1, 4), (2, 4), (2, 5), (3, 5), (4, 6), (5, 6)])
    G.name = 'Pyramid of height 2'
    F = PebblingFormula(G)
    lib = F.dimacs(export_header=False)
    cli = cnfgen(["cnfgen", "-q", "peb", "--pyramid", 2], mode='string')
    assert lib == cli
