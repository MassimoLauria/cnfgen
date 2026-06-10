import pytest
from io import StringIO as sio
from itertools import combinations,product

from cnfgen import CNF
from cnfgen import CliqueFormula
from cnfgen import RamseyWitnessFormula
from cnfgen import SubgraphFormula
from cnfgen import BinaryCliqueFormula

from cnfgen.graphs import readGraph, Graph

from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs, assertSAT, assertUNSAT

example1 = """
3
1 : 2 3 0
2 : 1 0
3 : 1 0
"""

example1alt = """
3
1 : 3 0
2 : 3 0
3 : 1 2 0
"""



def test_non_symmetric_input_wrong():
    """Symmetric encoding on non-symmetric graph

    The formula in this test uses the symmetric encoding for a non
    symmetric graph. This causes the formula to be unsatisfiable,
    even if it should be SAT.

    """
    G = readGraph(sio(example1), "simple", file_format="kthlist")
    T = readGraph(sio(example1alt), "simple", file_format="kthlist")
    F = SubgraphFormula(G, T,
                        symbreak=True)  # This should cause the wrong answer
    assertUNSAT(F)


def test_non_symmetric_input_right():
    """Symmetric encoding on non-symmetric graph

    The formula in this test uses the NON symmetric encoding for
    a non symmetric graph. This causes the formula to be
    satisfiable, as it should be.

    """
    G = readGraph(sio(example1), "simple", file_format="kthlist")
    T = readGraph(sio(example1alt), "simple", file_format="kthlist")
    F = SubgraphFormula(G, T)
    assertSAT(F)


def test_empty_in_complete_non_induced():
    """Check a tricky case in the implementation

    If the formula uses non symmetric encoding for the subset of
    vertices, then also the part of the formula about matching the
    edges requires non symmetric encoding.

    This checks that both parts are implemented correctly.
    """
    G = Graph.complete_graph(4)
    T = Graph.empty_graph(3)
    F = SubgraphFormula(G, T)
    assertSAT(F)

def test_empty_in_complete_induced():
    """Check a tricky case in the implementation

    If the formula uses non symmetric encoding for the subset of
    vertices, then also the part of the formula about matching the
    edges requires non symmetric encoding.

    This checks that both parts are implemented correctly.
    """
    G = Graph.complete_graph(4)
    T = Graph.empty_graph(3)
    F = SubgraphFormula(G, T, induced=True)
    assertUNSAT(F)


def test_induced_min_unsat():
    G = Graph.complete_graph(4)
    T = Graph.empty_graph(4)
    skipone=1
    for u,v in combinations(T.vertices(), 2):
        if skipone:
            skipone=0
            continue
        T.add_edge(u,v)
    F = SubgraphFormula(G, T, induced=True)
    assertUNSAT(F)


def test_not_symmetric_but_break():
    G = Graph.empty_graph(4)
    T = Graph.empty_graph(4)
    G.add_edge(1,2)
    T.add_edge(2,3)
    F = SubgraphFormula(G, T, symbreak=True)
    assertUNSAT(F)

def test_not_symmetric_dont_break():
    G = Graph.empty_graph(4)
    T = Graph.empty_graph(4)
    G.add_edge(1,2)
    T.add_edge(2,3)
    F = SubgraphFormula(G, T, symbreak=False)
    assertSAT(F)


@pytest.mark.parametrize("base,template", product(range(2, 5), range(2, 5)))
def test_parameters(base, template):
    parameters = [
        "cnfgen", "-q", "subgraph", "-G", "complete", base, "-H",
        "complete", template
    ]
    G = Graph.complete_graph(base)
    H = Graph.complete_graph(template)
    F = SubgraphFormula(G, H)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli

    parameters = [
        "cnfgen", "-q", "subgraph", "-G", "complete", base, "-H",
        "empty", template
    ]
    G = Graph.complete_graph(base)
    H = Graph.empty_graph(template)
    F = SubgraphFormula(G, H)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli

def test_github_issue_115():
    F = cnfgen(['cnfgen','kcliquebin',3,'complete',3,2],
               mode='formula')
    assertUNSAT(F)


def test_kcliquebib5_complete_1_4():
    F = cnfgen(['cnfgen','kcliquebin',5,'complete',1,4],
               mode='formula')
    assertUNSAT(F)

def test_kcliquebin4_complete_1_4():
    F = cnfgen(['cnfgen','kcliquebin',4,'complete',1,4],
               mode='formula')
    assertSAT(F)

def test_kcliquebin2():
    G = Graph.empty_graph(2)
    F = BinaryCliqueFormula(G, 2)
    assertUNSAT(F)
