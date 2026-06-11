import pytest
from cnfgen import CNF, PebblingFormula
from cnfgen.graphs import DirectedGraph, dag_path, dag_pyramid,  dag_complete_binary_tree

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual


def test_null_graph():
    G = DirectedGraph(0)
    peb = PebblingFormula(G)
    assert peb.debug()
    assertCnfEqual(peb, CNF())


def test_single_vertex():
    G = DirectedGraph(1)
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    x = F.new_variable('x(1)')
    F.add_clause([x])
    F.add_clause([-x])
    assertCnfEqual(peb,F)


def test_path():

    G = dag_path(10)
    peb = PebblingFormula(G)
    assert peb.debug()

    F = CNF()
    x = F.new_block(11, label='x({})')
    F.add_clause([x(1)])
    for i in range(1, 11):
        F.add_clause([-x(i), x(i+1)])
    F.add_clause([-x(11)])
    assertCnfEqual(peb,F)


def test_star():
    G = DirectedGraph(10)
    for i in range(1, 10):
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
    G = DirectedGraph(10)
    for i in range(1,10):
        G.add_edge(i,i+1)
    G.add_edge(10,1)
    with pytest.raises(ValueError):
        PebblingFormula(G)


def test_tree():
    for sz in range(1, 5):
        G = dag_complete_binary_tree(sz)
        F = PebblingFormula(G)
        lib = F.to_dimacs()
        cli = cnfgen(["cnfgen", "-q", "peb", "tree", sz], mode='string')
        assert lib == cli


def test_pyramid():
    G = dag_pyramid(2)
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
