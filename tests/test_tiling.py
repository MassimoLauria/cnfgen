import networkx as nx
import pytest
from cnfgen import CNF, Tiling

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual

def test_null_graph():
    G = nx.Graph()
    tiling = Tiling(G)
    assert tiling.debug()
    F = CNF()
    assertCnfEqual(F, tiling)


def test_single_vertex():
    G = nx.Graph()
    G.add_node(1)
    tiling = Tiling(G)
    assert tiling.debug()

    F = CNF()
    F.add_variable('x_{1}')
    F.add_clause([(True, 'x_{1}')])
    assertCnfEqual(F, tiling)

def test_star():
    G = nx.Graph()
    G.add_node(10)
    for i in range(0, 10):
        G.add_node(i)
        G.add_edge(i, 10)
    tiling = Tiling(G)
    assert tiling.debug()

    F = CNF()
    for i in range(10):
        F.add_variable('x_{{{}}}'.format(i))
    for i in range(10):
        F.add_clause([(True, 'x_{{{}}}'.format(i)), (True, 'x_{10}')])
    F.add_clause([(True, 'x_{{{}}}'.format(i)) for i in range(11)])
    for i in range(11):
        for j in range(i):
            F.add_clause([(False, 'x_{{{}}}'.format(i)), (False, 'x_{{{}}}'.format(j))])
    assertCnfEqual(F, tiling)

def test_cycle():
    G = nx.Graph()
    for i in range(0, 10):
        G.add_node(i)
        G.add_edge(i, (i+1)%10)
    tiling = Tiling(G)
    assert tiling.debug()

    F = CNF()
    for i in range(10):
        F.add_variable('x_{{{}}}'.format(i))
    for i in range(10):
        F.add_clause([(True, 'x_{{{}}}'.format(i)),
                      (True, 'x_{{{}}}'.format((i+1)%10)),
                       (True, 'x_{{{}}}'.format((i+2)%10))])
        F.add_clause([(False, 'x_{{{}}}'.format(i)),
                      (False, 'x_{{{}}}'.format((i+1)%10))])
        F.add_clause([(False, 'x_{{{}}}'.format(i)),
                      (False, 'x_{{{}}}'.format((i+2)%10))])
    assertCnfEqual(F, tiling)

def test_tiling_grid_cli():
    cnfgen(["cnfgen", "-q", "tiling", "grid", "3", "3"], mode='string')
