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
