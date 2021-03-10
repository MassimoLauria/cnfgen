import networkx as nx
import pytest
from cnfgen import CNF, PebblingFormula

from cnfgen.clitools import cnfgen, CLIError
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
    x = F.new_variable('x(1)')
    F.add_clause([x])
    F.add_clause([-x])
    assertCnfEqual(peb,F)


def test_path():

    G = nx.path_graph(10, nx.DiGraph())
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    x = F.new_block(10, label='x({})')
    F.add_clause([x(1)])
    for i in range(1, 10):
        F.add_clause([-x(i), x(i+1)])
    F.add_clause([-x(10)])
    assertCnfEqual(peb,F)


def test_star():
    G = nx.DiGraph()
    G.add_node(10)
    for i in range(1, 10):
        G.add_node(i)
        G.add_edge(i, 10)
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    x = F.new_block(10, label='x({})')
    for i in range(1,10):
        F.add_clause([x(i)])
    F.add_clause([-x(i) for i in range(1,10)] + [x(10)])
    F.add_clause([-x(10)])
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
        lib = F.to_dimacs()
        cli = cnfgen(["cnfgen", "-q", "peb", "tree", sz], mode='string')
        assert lib == cli


def test_pyramid():
    G = nx.DiGraph()
    G.add_edges_from([(1, 4), (2, 4), (2, 5), (3, 5), (4, 6), (5, 6)])
    G.name = 'Pyramid of height 2'
    F = PebblingFormula(G)
    lib = F.to_dimacs()
    cli = cnfgen(["cnfgen", "-q", "peb", "pyramid", 2], mode='string')
    assert lib == cli


def test_pebbling_pyramid_cli():
    cnfgen(["cnfgen", "-q", "peb", "pyramid", 2], mode='string')


def test_pebbling_pyramid_cli():
    cnfgen(["cnfgen", "-q", "peb", "tree", 2], mode='string')


def test_stone_pyramid_cli():
    cnfgen(["cnfgen", "-q", "stone", 5, "pyramid", 5], mode='string')


def test_stone_tree_cli():
    cnfgen(["cnfgen", "-q", "stone", 5, "tree", 3], mode='string')


def test_sstone_pyramid_cli():
    cnfgen(["cnfgen", "-q", "stone", 5, "pyramid", 5, "--sparse", 4],
           mode='string')


def test_sstone_tree_cli():
    cnfgen(["cnfgen", "-q", "stone", 5, "tree", 3, "--sparse", 3],
           mode='string')


def test_sstone_tree_cli():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "-q", "stone", 5, "tree", 3, "--sparse", 10],
               mode='string')
