#!/usr/bin/env python

import pytest

import cnfgen
from cnfgen.graphs import Graph, BipartiteGraph,DirectedGraph
from cnfgen.graphs import random_gnm,random_gnp,random_gnd,multipartite_random


def assert_d_regular(G:Graph,d):
    for v in G.vertices():
        assert len(G.adjlist[v])==d
        assert v not in G.adjlist[v]
        for w in G.adjlist[v]:
            assert v in G.adjlist[w]



def test_d_regular_nx():
    import networkx as nx
    G = nx.random_regular_graph(3,10)
    G = Graph.from_networkx(G)
    assert_d_regular(G,3)

def test_d_regular():
    G = random_gnd(30,3)
    assert_d_regular(G,3)
