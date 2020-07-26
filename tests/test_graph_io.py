#!/usr/bin/env python

from io import StringIO as sio
from io import BytesIO
import networkx as nx
import pytest

import cnfformula
from cnfformula.graphs import readGraph, writeGraph, supported_formats
from cnfformula.graphs import bipartite_sets, has_dot_library

from tests.utils import example_filename

dot_path2 = 'graph G { 0 -- 1 -- 2}'
gml_path2 = """
        graph [
           node [
             id 0
             label 0
           ]
           node [
             id 1
             label 1
           ]
           node [
             id 2
             label 2
           ]
           edge [
             source 0
             target 1
           ]
           edge [
             source 1
             target 2
           ]
         ]"""

dimacs_path2 = "p edge 3 2\ne 1 2\ne 2 3\n"

kthlist_non_bipartite = """
5
1: 2 3 0
5: 3 4 0
4: 5 0
2: 3 0
"""

kthlist_non_dag = """
3
1: 2 0
2: 3 0
3: 1 0
"""
kthlist_bipartite = """
5
1: 2 0
2: 1 0
3: 0
4: 1 0
"""


def test_low_level_dot_read_path2():

    if not has_dot_library():
        pytest.skip("DOT library not installed. Can't test DOT I/O")

    G = nx.Graph(nx.nx_pydot.read_dot(sio(dot_path2)))

    assert G.order() == 3
    assert len(G.edges()) == 2
    assert G.has_edge('0', '1')
    assert G.has_edge('1', '2')
    assert not G.has_edge('0', '2')


def test_low_level_dot_broken_TypeError():

    if not has_dot_library():
        pytest.skip("DOT library not installed. Can't test DOT I/O")

    with pytest.raises(TypeError):
        nx.Graph(nx.nx_pydot.read_dot(sio("jsjd jfdakh jkad ")))


def test_low_level_gml_read_path2():

    G = nx.read_gml(BytesIO(gml_path2.encode("ascii")))

    assert G.order() == 3
    assert len(G.edges()) == 2
    assert G.has_edge(0, 1)
    assert G.has_edge(1, 2)
    assert not G.has_edge(0, 2)


def test_low_level_gml_broken_NetworkXError():

    with pytest.raises(nx.exception.NetworkXError):
        nx.read_gml(BytesIO(b"jsjd jfdakh jkad "))


def test_low_level_dimacs_read_path2():

    G = cnfformula.graphs._read_graph_dimacs_format(sio(dimacs_path2))

    assert G.order() == 3
    assert len(G.edges()) == 2
    assert G.has_edge(1, 2)
    assert G.has_edge(2, 3)
    assert not G.has_edge(1, 3)


def test_readGraph_dot_path2():

    if 'dot' not in supported_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    with pytest.raises(ValueError):
        readGraph(sio(dot_path2), graph_type='simple')

    G = readGraph(sio(dot_path2), graph_type='simple', file_format='dot')
    assert G.order() == 3
    assert len(G.edges()) == 2


def test_readGraph_gml_path2():

    with pytest.raises(ValueError):
        readGraph(sio(gml_path2), graph_type='simple')

    G = readGraph(sio(gml_path2), graph_type='simple', file_format='gml')
    assert G.order() == 3
    assert len(G.edges()) == 2


def test_readGraph_dimacs_path2():

    with pytest.raises(ValueError):
        readGraph(sio(dimacs_path2), graph_type='simple')

    G = readGraph(sio(dimacs_path2), graph_type='simple', file_format='dimacs')
    assert G.order() == 3
    assert len(G.edges()) == 2


def test_readGraph_kthlist_non_dag():

    with pytest.raises(ValueError):
        readGraph(sio(kthlist_non_dag), graph_type='digraph')

    with pytest.raises(ValueError):
        readGraph(sio(kthlist_non_dag),
                  graph_type='dag',
                  file_format='kthlist')

    G = readGraph(sio(kthlist_non_dag),
                  graph_type='digraph',
                  file_format='kthlist')

    assert G.order() == 3
    assert len(G.edges()) == 3


def test_readGraph_kthlist_non_bipartite():

    with pytest.raises(ValueError):
        readGraph(sio(kthlist_non_bipartite), graph_type='bipartite')

    with pytest.raises(ValueError):
        readGraph(sio(kthlist_non_bipartite),
                  graph_type='bipartite',
                  file_format='kthlist')

    G = readGraph(sio(kthlist_non_bipartite),
                  graph_type='simple',
                  file_format='kthlist')

    assert G.order() == 5
    assert len(G.edges()) == 5

    with pytest.raises(ValueError):
        bipartite_sets(G)


def test_readGraph_kthlist_bipartite():

    G = readGraph(sio(kthlist_bipartite),
                  graph_type='bipartite',
                  file_format='kthlist')

    assert G.order() == 5

    L, R = bipartite_sets(G)
    assert len(L) == 2
    assert len(R) == 3


def test_readGraph_dot_file_as_gml():

    if 'dot' not in supported_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    with open(example_filename('path2.dot'), 'r') as ifile:
        # Parsing should fail here
        with pytest.raises(ValueError):
            readGraph(ifile, graph_type='simple', file_format='gml')


def test_readGraph_dot_file_remember_name():
    """Even if we are reading the file from a IO stream, we still remember
the original file name so we can guess the format."""
    if 'dot' not in supported_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    with open(example_filename('path2.dot'), 'r') as ifile:
        # Parser should guess that it is a dot file
        G = readGraph(ifile, graph_type='simple')
        assert G.order() == 3
        assert len(G.edges()) == 2


def test_undoable_io():

    # assumes that 'does_not_exist.gml' does not exist in the working directory
    with pytest.raises(IOError):
        readGraph("does_not_exist.gml", graph_type='simple')

    # assumes that '/does_not_exist.gml' is not writable
    with pytest.raises(IOError):
        writeGraph(nx.Graph(), "/does_not_exist.gml", graph_type='simple')
