import pytest
from cnfgen import CNF, Tiling
from cnfgen.graphs import Graph

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual

def test_null_graph():
    G = Graph.null_graph()
    tiling = Tiling(G)
    assert tiling.debug()
    F = CNF()
    assertCnfEqual(F, tiling)


def test_single_vertex():
    G = Graph(1)
    tiling = Tiling(G)
    assert tiling.debug()

    F = CNF()
    x = F.new_variable('x_{1}')
    print(*F.all_variable_labels())
    F.add_clause([x])
    assertCnfEqual(tiling, F)

def test_star():
    G = Graph(10)
    for i in range(1, 10):
        G.add_edge(i, 10)
    tiling = Tiling(G)
    assert tiling.debug()
    print(list(tiling.clauses()))

    F = CNF()
    x = F.new_block(10, label='x_{{{}}}')
    F.add_linear(x(None), '==', 1)
    assert len(F) == 46
    for i in range(1,10):
        F.add_linear([x(i),x(10)], '==', 1)
    assert len(F) == 46 + 9*2

    print(list(F.clauses()))
    assertCnfEqual(tiling,F)

def test_cycle():
    G = Graph(10)
    for i in range(1, 10):
        G.add_edge(i, i+1)
    G.add_edge(10, 1)
    tiling = Tiling(G)
    assert tiling.debug()

    F = CNF()
    x = F.new_block(10, label='x_{{{}}}')
    for i in range(1, 9):
        F.add_linear([x(i), x(i + 1), x(i+2)], '==', 1)
    F.add_linear([x(1), x(9), x(10)], '==', 1)
    F.add_linear([x(1), x(2), x(10)], '==', 1)
    assertCnfEqual(F, tiling)


def test_tiling_grid3_cli():
    F = cnfgen(["cnfgen", "-q", "tiling", "grid", 3, 3], mode='formula')
    assert not F.is_satisfiable()[0]

def test_tiling_grid4_cli():
    F = cnfgen(["cnfgen", "-q", "tiling", "grid", 4, 4], mode='formula')
    assert F.is_satisfiable()[0]
