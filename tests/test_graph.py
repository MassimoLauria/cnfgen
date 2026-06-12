#!/usr/bin/env python

import pytest

import cnfgen
from cnfgen.graphs import Graph, BipartiteGraph,DirectedGraph
from cnfgen.graphs import random_gnm,random_gnp,random_gnd,multipartite_random
from cnfgen.graphs import bipartite_random


def test_conversion_from_networkx():
    try:
        import networkx
    except:
        pytest.skip("networkx not installed. Skip conversion test")

    G = networkx.bipartite.complete_bipartite_graph(5,7)
    B = BipartiteGraph.from_networkx(G)
    assert B.order() == 12
    assert B.left_order() == 5
    assert B.has_edge(2,3)


def test_conversion_to_networkx():
    try:
        import networkx
    except:
        pytest.skip("networkx not installed. Skip conversion test")

    G = networkx.bipartite.complete_bipartite_graph(5,7)
    B = bipartite_random(5,4,0.3)
    D = B.to_networkx().nodes(data=True)
    assert D[1]['bipartite']==0
    assert D[5]['bipartite']==0
    assert D[6]['bipartite']==1
    assert D[9]['bipartite']==1


def assert_d_regular(G:Graph,d):
    for v in G.vertices():
        assert len(G.adjlist[v])==d
        assert v not in G.adjlist[v]
        for w in G.adjlist[v]:
            assert v in G.adjlist[w]



def test_d_regular():
    for d in range(10):
        G = random_gnd(10,d)
        assert_d_regular(G,d)


def test_d_regular_odd():
    G = random_gnd(11,6)
    assert_d_regular(G,6)

def test_d_regular_odd_bad():
    with pytest.raises(ValueError):
        G = random_gnd(11,5)

def test_d_regular_large():
    G = random_gnd(100,80)
    assert_d_regular(G,80)
