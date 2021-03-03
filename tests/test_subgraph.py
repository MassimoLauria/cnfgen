import pytest
import networkx as nx
from io import StringIO as sio
from itertools import combinations,product




from cnfgen import CNF
from cnfgen import CliqueFormula
from cnfgen import RamseyWitnessFormula
from cnfgen import SubgraphFormula

from cnfgen.graphs import readGraph, normalize_networkx_labels

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
    G = nx.complete_graph(4)
    T = nx.empty_graph(3)
    normalize_networkx_labels(G)
    normalize_networkx_labels(T)
    F = SubgraphFormula(G, T)
    assertSAT(F)

def test_empty_in_complete_induced():
    """Check a tricky case in the implementation

    If the formula uses non symmetric encoding for the subset of
    vertices, then also the part of the formula about matching the
    edges requires non symmetric encoding.

    This checks that both parts are implemented correctly.
    """
    G = nx.complete_graph(4)
    T = nx.empty_graph(3)
    G = normalize_networkx_labels(G)
    T = normalize_networkx_labels(T)
    F = SubgraphFormula(G, T, induced=True)
    assertUNSAT(F)


def test_induced_min_unsat():
    G = nx.complete_graph(4)
    T = nx.empty_graph(4)
    G = normalize_networkx_labels(G)
    T = normalize_networkx_labels(T)
    edges = list(combinations(T.nodes(), 2))
    print(edges)
    T.add_edges_from(edges[1:])
    F = SubgraphFormula(G, T, induced=True)
    assertUNSAT(F)


def test_not_symmetric_but_break():
    G = nx.empty_graph(4)
    G = normalize_networkx_labels(G)
    T = nx.empty_graph(4)
    T = normalize_networkx_labels(T)
    G.add_edge(1,2)
    T.add_edge(2,3)
    F = SubgraphFormula(G, T, symbreak=True)
    assertUNSAT(F)

def test_not_symmetric_dont_break():
    G = nx.empty_graph(4)
    G = normalize_networkx_labels(G)
    T = nx.empty_graph(4)
    T = normalize_networkx_labels(T)
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
    G = nx.complete_graph(base)
    H = nx.complete_graph(template)
    G = normalize_networkx_labels(G)
    H = normalize_networkx_labels(H)
    F = SubgraphFormula(G, H)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli

    parameters = [
        "cnfgen", "-q", "subgraph", "-G", "complete", base, "-H",
        "empty", template
    ]
    G = nx.complete_graph(base)
    H = nx.empty_graph(template)
    G = normalize_networkx_labels(G)
    H = normalize_networkx_labels(H)
    F = SubgraphFormula(G, H)
    lib = F.to_dimacs()
    cli = cnfgen(parameters, mode='string')
    assert lib == cli
