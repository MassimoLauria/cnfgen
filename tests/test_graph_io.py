#!/usr/bin/env python

from io import StringIO as sio
from io import BytesIO
import networkx as nx
import pytest

import cnfgen
from cnfgen.clitools import CLIError
from cnfgen.graphs import readGraph, writeGraph, supported_graph_formats
from cnfgen.graphs import has_dot_library
from cnfgen.graphs import Graph, BipartiteGraph,DirectedGraph

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
2: 3 0
4: 5 0
5: 3 4 0
"""

kthlist_non_dag = """
3
1: 2 0
2: 3 0
3: 1 0
"""

kthlist_dag = """
3
1: 0
2: 1 0
3: 2 0
"""


kthlist_bipartite_non_strict = """
5
1: 2 0
2: 1 0
3: 0
4: 1 0
"""

kthlist_bipartite_strict = """
5
1: 3 0
2: 4 0
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

    G = cnfgen.graphs._read_graph_dimacs_format(sio(dimacs_path2),Graph)

    assert isinstance(G,Graph)
    assert G.order() == 3
    assert len(G.edges()) == 2
    assert G.has_edge(1, 2)
    assert G.has_edge(2, 3)
    assert not G.has_edge(1, 3)


def test_readGraph_dot_path2():

    if 'dot' not in supported_graph_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    with pytest.raises(ValueError):
        readGraph(sio(dot_path2), graph_type='simple')

    G = readGraph(sio(dot_path2), graph_type='simple', file_format='dot')
    assert isinstance(G, Graph)
    assert G.order() == 3
    assert len(G.edges()) == 2


def test_readGraph_gml_path2():

    with pytest.raises(ValueError):
        readGraph(sio(gml_path2), graph_type='simple')

    G = readGraph(sio(gml_path2), graph_type='simple', file_format='gml')
    assert isinstance(G, Graph)
    assert G.order() == 3
    assert len(G.edges()) == 2


def test_readGraph_dimacs_path2():

    with pytest.raises(ValueError):
        readGraph(sio(dimacs_path2), graph_type='simple')

    G = readGraph(sio(dimacs_path2), graph_type='simple', file_format='dimacs')
    assert isinstance(G, Graph)
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
    assert isinstance(G, DirectedGraph)
    assert G.order() == 3
    assert len(G.edges()) == 3


def test_readGraph_kthlist_dag():

    G = readGraph(sio(kthlist_dag),
                  graph_type='dag',
                  file_format='kthlist')
    assert isinstance(G, DirectedGraph)
    assert G.order() == 3
    assert len(G.edges()) == 2


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
    assert isinstance(G, Graph)
    assert G.order() == 5
    assert len(G.edges()) == 5

    with pytest.raises(AttributeError):
        G.parts()


# Old version would accept non strict kthlists
# I decided to drop that
def test_readGraph_kthlist_bipartite_non_strict():

    with pytest.raises(ValueError):
        readGraph(sio(kthlist_bipartite_non_strict),
                  graph_type='bipartite',
                  file_format='kthlist')


def test_readGraph_kthlist_bipartite_strict():

    G = readGraph(sio(kthlist_bipartite_strict),
                  graph_type='bipartite',
                  file_format='kthlist')

    assert isinstance(G, BipartiteGraph)
    assert G.order() == 5

    L, R = G.parts()
    assert len(L) == 2
    assert len(R) == 3
    assert G.has_edge(1, 1)
    assert not G.has_edge(1, 2)
    assert not G.has_edge(1, 3)
    assert not G.has_edge(2, 1)
    assert G.has_edge(2, 2)
    assert not G.has_edge(2, 3)


def test_readGraph_dot_file_as_gml(shared_datadir):

    if 'dot' not in supported_graph_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    fname = str(shared_datadir / 'path2.dot')
    with open(fname, 'r') as ifile:
        # Parsing should fail here
        with pytest.raises(ValueError):
            readGraph(ifile, graph_type='simple', file_format='gml')


def test_readGraph_dot_file_remember_name(shared_datadir):
    """Even if we are reading the file from a IO stream, we still remember
the original file name so we can guess the format."""
    if 'dot' not in supported_graph_formats()['simple']:
        pytest.skip("No support for Dot file I/O.")

    fname = str(shared_datadir / 'path2.dot')
    with open(fname) as ifile:
        # Parser should guess that it is a dot file
        G = readGraph(ifile, graph_type='simple')
        assert isinstance(G, Graph)
        assert G.order() == 3
        assert len(G.edges()) == 2


def test_write_graph_typecheck():
    with pytest.raises(TypeError):
        G = nx.Graph()
        writeGraph(G, "/does_not_exist.gml", graph_type='simple')

def test_undoable_io():

    # assumes that 'does_not_exist.gml' does not exist in the working directory
    with pytest.raises(IOError):
        readGraph("does_not_exist.gml", graph_type='simple')

    # assumes that '/does_not_exist.gml' is not writable
    with pytest.raises(IOError):
        G = Graph(4)
        writeGraph(G, "/does_not_exist.gml", graph_type='simple')


def test_cli_filenotfound():

    # assumes that 'does_not_exist.gml' does not exist in the working directory
    with pytest.raises(CLIError):
        cnfgen.cnfgen(['cnfgen', 'gop', 'does_not_exists.gml'], mode='string')


def test_readGraph_bipartite_good_kthlist(shared_datadir):

    filename = "bipartite_good.kthlist"
    B = readGraph(str(shared_datadir / filename), graph_type='bipartite')
    assert B.order() == 7
    assert B.left_order() == 4
    assert B.right_order() == 3
    assert B.number_of_edges() == 7


def test_readGraph_bipartite_good_matrix(shared_datadir):

    filename = "bipartite_good.matrix"
    B = readGraph(str(shared_datadir / filename), graph_type='bipartite')
    assert B.order() == 7
    assert B.left_order() == 4
    assert B.right_order() == 3
    assert B.number_of_edges() == 8


def test_readGraph_bipartite_good_dot(shared_datadir):

    filename = "bipartite_good.dot"
    B = readGraph(str(shared_datadir / filename), graph_type='bipartite')
    assert B.order() == 7
    assert B.left_order() == 4
    assert B.right_order() == 3
    assert B.number_of_edges() == 6


def test_readGraph_bipartite_good_gml(shared_datadir):

    filename = "bipartite_good.gml"
    B = readGraph(str(shared_datadir / filename), graph_type='bipartite')
    assert B.order() == 7
    assert B.left_order() == 4
    assert B.right_order() == 3
    assert B.number_of_edges() == 7


def test_readGraph_bipartite_bad_monoedge_dot(shared_datadir):

    if not has_dot_library():
        pytest.skip("DOT library not installed. Can't test DOT I/O")

    filename = "bipartite_bad_monoedge.dot"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')


def test_readGraph_bipartite_bad_bipartition_dot(shared_datadir):

    if not has_dot_library():
        pytest.skip("DOT library not installed. Can't test DOT I/O")

    filename = "bipartite_bad_bipartition.dot"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')


def test_readGraph_bipartite_bad_bipartition2_dot(shared_datadir):

    if not has_dot_library():
        pytest.skip("DOT library not installed. Can't test DOT I/O")

    filename = "bipartite_bad_bipartition2.dot"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')


def test_readGraph_bipartite_bad_monoedge_gml(shared_datadir):

    filename = "bipartite_bad_monoedge.gml"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')


def test_readGraph_bipartite_bad_bipartition_gml(shared_datadir):

    filename = "bipartite_bad_bipartition.gml"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')


def test_readGraph_bipartite_bad_bipartition2_monoedge_gml(shared_datadir):

    filename = "bipartite_bad_bipartition2.gml"
    with pytest.raises(ValueError):
        readGraph(str(shared_datadir / filename), graph_type='bipartite')
