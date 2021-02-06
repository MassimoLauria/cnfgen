import pytest

from cnfgen.graphs import has_bipartition
from cnfgen.graphs import CompleteBipartiteGraph
from cnfgen.graphs import BipartiteGraph


def test_build_bipartite():
    G = BipartiteGraph(3, 4)
    assert len(G) == 7
    assert G.left_order() == 3
    assert G.right_order() == 4
    assert not G.has_edge(2, 1)
    G.add_edge(1, 2)
    G.add_edge(3, 4)
    assert len(G.edges()) == 2
    left, right = G.parts()
    assert len(left) == 3
    assert len(right) == 4
    assert (1, 2) in G.edges()
    assert (3, 4) in G.edges()
    assert (2, 1) not in G.edges()
    assert has_bipartition(G)


def test_complete_bipartite():
    G = CompleteBipartiteGraph(5, 5)
    assert len(G) == 10
    assert G.left_order() == 5
    assert G.right_order() == 5
    assert G.has_edge(2, 1)
    assert G.has_edge(5, 5)
    assert len(G.edges()) == 25
    assert (1, 2) in G.edges()
    assert (3, 4) in G.edges()
    assert (5, 5) in G.edges()
    assert has_bipartition(G)


def test_empty_bipartite():
    G1 = CompleteBipartiteGraph(0, 5)
    G2 = CompleteBipartiteGraph(5, 0)
    G3 = CompleteBipartiteGraph(0, 0)
    assert len(G1) == 5
    assert len(G2) == 5
    assert len(G3) == 0
    assert len(G1.edges()) == 0
    assert len(G2.edges()) == 0
    assert len(G3.edges()) == 0
