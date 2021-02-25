"""Tests for the command line constructions for simple graphs"""
import pytest

from cnfgen.clitools.graph_args import parse_graph_argument
from cnfgen.clitools.graph_args import obtain_graph


def M(graphspec):
    "Quickly makes a graph from the specs"
    parser = parse_graph_argument('simple', graphspec)
    return obtain_graph(parser)

def test_empty():
    G = M("empty 10")
    assert G.order() == 10
    assert list(G.nodes()) == list(range(1,11))



def test_gnp():
    G = M("gnp  10 0.5")
    assert G.order() == 10


def test_gnm():
    G = M("gnm  10 15")
    assert G.order() == 10
    assert G.size() == 15


def test_gnd_fail():
    with pytest.raises(ValueError):
        M("gnd 9 3")


def test_complete():
    G = M("complete 10")
    assert G.order() == 10
    assert G.size() == 45
    for v in G.nodes():
        assert G.degree(v) == 9


def test_complete_multipartite():
    G = M("complete 5 4")
    assert G.order() == 20
    assert G.size() == 150
    for v in G.nodes():
        assert G.degree(v) == 15


def test_complete_fail0():
    with pytest.raises(ValueError):
        M("complete")


def test_complete_fail3():
    with pytest.raises(ValueError):
        M("complete 2 2 2 ")


def test_grid():
    G = M("grid 8 5")
    assert G.order() == 40
    degrees = sorted([G.degree(v) for v in G.nodes()])

    assert degrees == [2] * 4 + [3] * (3 + 3 + 6 + 6) + [4] * (3 * 6)


def test_grid2():
    G = M('grid 3 4 2')
    assert G.order() == 3*4*2


def test_complete_multipartite_random():
    G = M('gnp 5 1.0 3')
    assert G.order() == 5*3
    assert G.number_of_edges() == 3 * 5 * 5


def test_multipartite():
    G = M('gnp 5 1.0 3')
    assert G.order() == 5*3


def test_regular():
    G = M('gnd 10 3')
    assert G.order() == 10
    assert G.number_of_edges() == 10 * 3 // 2


def test_torus():
    G = M("torus 8 5")
    assert G.order() == 40

    for v in G.nodes():
        assert G.degree(v) == 4


def test_already_complete_addedge():
    with pytest.raises(ValueError):
        M("complete 10 addedges 1")


def test_empty_to_complete():
    G = M("gnp 10 0 addedges 45")
    assert G.order() == 10
    assert G.size() == 45
    for v in G.nodes():
        assert G.degree(v) == 9


def test_add_edges():
    G = M("gnm 10  15  addedges 10")
    assert G.order() == 10
    assert G.size() == 25


def test_plant_too_large():
    with pytest.raises(ValueError):
        M("complete 10 plantclique 11")


def test_already_complete_plant():
    G = M("complete 10 plantclique 5")
    assert G.order() == 10
    assert G.size() == 45


def test_complete_with_planted():
    G = M("gnp 10 0.3 plantclique 10")
    assert G.order() == 10
    assert G.size() == 45


def test_plant_clique():
    G = M("gnm 10 15 plantclique 6")
    assert G.order() == 10
    assert 15 <= G.size() <= 30
