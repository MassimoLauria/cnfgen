"""Tests for the command line constructions for simple graphs"""
import pytest

from cnfgen.clitools.graph_args import parse_graph_argument
from cnfgen.clitools.graph_args import obtain_graph

def DI(graphspec):
    "Quickly makes a graph from the specs"
    parser = parse_graph_argument('digraph', graphspec)
    return obtain_graph(parser)

def test_tree0():
    G = DI("tree 0")
    assert list(G.nodes()) == [1]
    assert G.number_of_edges() == 0
    assert G.is_dag()

def test_tree1():
    G = DI("tree 1")
    assert list(G.nodes()) == [1, 2, 3]
    assert G.number_of_edges() == 2
    assert G.is_dag()
    assert G.has_edge(1, 3)
    assert G.has_edge(2, 3)

def test_tree4():
    G = DI("tree 4")
    assert G.order() == 31
    assert list(G.nodes()) == list(range(1, 32))
    assert G.number_of_edges() == 30
    assert G.is_dag()


def test_path0():
    G = DI("path 0")
    assert G.order() == 1
    assert list(G.nodes()) == [1]
    assert G.number_of_edges() == 0
    assert G.is_dag()

def test_path1():
    G = DI("path 1")
    assert list(G.nodes()) == [1,2]
    assert G.number_of_edges() == 1
    assert G.is_dag()

def test_path4():
    G = DI("path 4")
    assert list(G.nodes()) == [1,2,3,4,5]
    assert G.number_of_edges() == 4
    assert G.is_dag()

def test_pyramid0():
    G = DI("pyramid 0")
    assert list(G.nodes()) == [1]
    assert G.number_of_edges() == 0
    assert G.is_dag()

def test_pyramid1():
    G = DI("pyramid 1")
    assert list(G.nodes()) == [1,2,3]
    assert G.number_of_edges() == 2
    assert G.is_dag()
    assert G.has_edge(1, 3)
    assert G.has_edge(2, 3)

def test_pyramid5():
    G = DI("pyramid 5")
    assert list(G.nodes()) == list(range(1,22))
    assert G.number_of_edges() == (21 - 6)* 2
    assert G.is_dag()
    assert G.has_edge(1, 7)
    assert G.has_edge(2, 7)
    assert G.has_edge(2, 8)
    assert G.has_edge(3, 8)
    assert G.has_edge(3, 9)
    assert G.has_edge(4, 9)
    assert G.has_edge(4, 10)
    assert G.has_edge(5, 10)
    assert G.has_edge(5, 11)
    assert G.has_edge(5, 11)
    assert G.has_edge(19, 21)
    assert G.has_edge(20, 21)
