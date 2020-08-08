import networkx as nx
from io import StringIO as sio
from itertools import combinations

from cnfgen import CNF
from cnfgen import SubgraphFormula
from cnfgen import CliqueFormula
from cnfgen import RamseyWitnessFormula

from cnfgen.graphs import readGraph, writeGraph

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


def test_no_templates():
    """No templates graphs should generate an empty fomula
    """
    dimacs = """\
    p cnf 0 0
    """
    G = nx.complete_graph(4)
    F = SubgraphFormula(G, [])
    assertCnfEqualsDimacs(F, dimacs)


def test_non_symmetric_input_wrong():
    """Symmetric encoding on non-symmetric graph

    The formula in this test uses the symmetric encoding for a non
    symmetric graph. This causes the formula to be unsatisfiable,
    even if it should be SAT.

    """
    G = readGraph(sio(example1), "simple", file_format="kthlist")
    T = readGraph(sio(example1alt), "simple", file_format="kthlist")
    F = SubgraphFormula(G, [T],
                        symmetric=True)  # This should cause the wrong answer
    assertUNSAT(F)


def test_non_symmetric_input_right():
    """Symmetric encoding on non-symmetric graph

    The formula in this test uses the NON symmetric encoding for
    a non symmetric graph. This causes the formula to be
    satisfiable, as it should be.

    """
    G = readGraph(sio(example1), "simple", file_format="kthlist")
    T = readGraph(sio(example1alt), "simple", file_format="kthlist")
    F = SubgraphFormula(G, [T])
    assertSAT(F)


def test_non_symmetric_clause_generator():
    """Check a tricky case in the implementation

    If the formula uses non symmetric encoding for the subset of
    vertices, then also the part of the formula about matching the
    edges requires non symmetric encoding.

    This checks that both parts are implemented correctly.
    """
    G = nx.complete_graph(4)
    T = nx.empty_graph(4)
    F = SubgraphFormula(G, [T])
    assertUNSAT(F)


def test_non_symmetric_min_unsat():
    G = nx.complete_graph(4)
    T = nx.empty_graph(4)
    edges = list(combinations(G.nodes(), 2))
    T.add_edges_from(edges[1:])
    F = SubgraphFormula(G, [T])
    assertUNSAT(F)


def test_symmetric_min_unsat():
    G = nx.empty_graph(4)
    G.add_edge(0, 1)
    T = nx.empty_graph(4)
    F = SubgraphFormula(G, [T])
    assertUNSAT(F)


def test_parameters():
    for base in range(2, 5):
        for template in range(2, 5):
            parameters = [
                "cnfgen", "-q", "subgraph", "--complete", base, "--completeT",
                template
            ]
            G = nx.complete_graph(base)
            T = nx.complete_graph(template)
            F = SubgraphFormula(G, [T])
            lib = F.dimacs(export_header=False)
            cli = cnfgen(parameters, mode='string')
            assert lib == cli

            parameters = [
                "cnfgen", "-q", "subgraph", "--complete", base, "--emptyT",
                template
            ]
            G = nx.complete_graph(base)
            T = nx.empty_graph(template)
            F = SubgraphFormula(G, [T])
            lib = F.dimacs(export_header=False)
            cli = cnfgen(parameters, mode='string')
            assert lib == cli
