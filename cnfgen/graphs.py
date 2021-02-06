#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to manage graph formats and graph files in order to build
formulas that are graph based.
"""

import copy
__all__ = [
    "supported_formats", "readGraph", "writeGraph", "is_dag",
    "enumerate_vertices", "enumerate_edges", "neighbors",
    "bipartite_random_left_regular", "bipartite_random_regular",
    "bipartite_random_m_edges", "bipartite_random", "dag_complete_binary_tree",
    "dag_pyramid"
]

#################################################################
#          Graph Decoders (first is default)
#################################################################

_graphformats = {
    'dag': ['kthlist', 'gml', 'dot'],
    'digraph': ['kthlist', 'gml', 'dot', 'dimacs'],
    'simple': ['kthlist', 'gml', 'dot', 'dimacs'],
    'bipartite': ['kthlist', 'matrix', 'gml', 'dot']
}


def supported_formats():
    """The graph file formats supported by the library."""
    return copy.deepcopy(_graphformats)


#################################################################
#          Import third party code
#################################################################

import sys
from io import StringIO, BytesIO
import io
import os
import fileinput
import networkx

from itertools import product


class EdgeList():
    """Edge list for bipartite graphs"""
    def __init__(self, B):
        self.B = B

    def __len__(self):
        return self.B.edgecount

    def __contains__(self, t):
        return len(t) == 2 and self.B.has_edge(t[0], t[1])

    def __iter__(self):
        for u in range(1, self.B.left_order() + 1):
            yield from ((u, v) for v in self.B.right_neighbors(u))


def has_bipartition(G):
    """Return the bipartition of the vertices

    Raises 'ValueError' if bipartition labels are missing"""
    return isinstance(G, BaseBipartiteGraph)


class BaseBipartiteGraph():
    def __init__(self, L, R):
        if L < 0 or R < 0:
            raise ValueError(
                "Left and right size of the bipartite graph must be non-negative"
            )
        self.lorder = L
        self.rorder = R
        self.name = 'Bipartite graph with ({},{}) vertices'.format(L, R)

    def order(self):
        return self.lorder + self.rorder

    def size(self):
        return len(self.edges())

    def number_of_edges(self):
        return self.size()

    def left_order(self):
        return self.lorder

    def right_order(self):
        return self.rorder

    def left_degree(self, v):
        return len(self.left_neighbors(v))

    def right_degree(self, u):
        return len(self.right_neighbors(u))

    def left_neighbors(self, v):
        raise NotImplementedError

    def right_neighbors(self, u):
        raise NotImplementedError

    def parts(self):
        return range(1, self.lorder + 1), range(1, self.rorder + 1)

    def has_edge(self):
        raise NotImplementedError

    def add_edge(self):
        raise NotImplementedError

    def add_edges_from(self, edges):
        for u, v in edges:
            self.add_edge(u, v)

    def edges(self):
        return EdgeList(self)

    def __len__(self):
        return self.order()

    @staticmethod
    def from_networkx(G):
        left = []
        right = []
        left_ids = {}
        right_ids = {}
        try:
            for n in G.nodes():
                color = G.nodes[n]['bipartite']
                if color in [0, '0']:
                    left.append(n)
                elif color in [1, '1']:
                    right.append(n)
                else:
                    raise KeyError
        except KeyError:
            raise ValueError(
                "Full bipartition is missing, each vertex must have a 0,1 label."
            )
        B = BipartiteGraph(len(left), len(right))
        left.sort()
        right.sort()
        left_ids = {u: i for (i, u) in enumerate(left, start=1)}
        right_ids = {v: i for (i, v) in enumerate(right, start=1)}
        for u, v in G.edges():
            B.add_edge(left_ids[u], right_ids[v])
        return B


class BipartiteGraph(BaseBipartiteGraph):
    def __init__(self, L, R):
        BaseBipartiteGraph.__init__(self, L, R)
        self.ladj = {}
        self.radj = {}
        self.edgecount = 0

    def has_edge(self, u, v):
        return u in self.ladj and v in self.ladj[u]

    def add_edge(self, u, v):
        """Add an edge to the graph.
        
        - allows multi-edges (i.e. multiple occurrences are allowed)
        - neighbors of a vertex are kept in insertion order
        """
        if not (1 <= u <= self.lorder and 1 <= v <= self.rorder):
            raise ValueError("Invalid choice of vertices")
        if u not in self.ladj:
            self.ladj[u] = []
        if v not in self.radj:
            self.radj[v] = []
        self.ladj[u].append(v)
        self.radj[v].append(u)
        self.edgecount += 1

    def right_neighbors(self, u):
        if not (1 <= u <= self.lorder):
            raise ValueError("Invalid choice of vertex")
        return self.ladj.get(u, [])[:]

    def left_neighbors(self, v):
        if not (1 <= v <= self.rorder):
            raise ValueError("Invalid choice of vertex")
        return self.radj.get(v, [])[:]


class CompleteBipartiteGraph(BaseBipartiteGraph):
    def __init__(self, L, R):
        BaseBipartiteGraph.__init__(self, L, R)
        self.edgecount = L * R
        self.name = 'Complete bipartite graph with ({},{}) vertices'.format(
            L, R)

    def has_edge(self, u, v):
        return (1 <= u <= self.lorder and 1 <= v <= self.rorder)

    def add_edge(self, u, v):
        pass

    def right_neighbors(self, u):
        return range(1, self.rorder + 1)

    def left_neighbors(self, v):
        return range(1, self.lorder + 1)


def has_dot_library():
    """Test the presence of pydot
    """
    try:
        # newer version of networkx
        from networkx import nx_pydot
        import pydot
        del pydot
        return True
    except ImportError:
        pass

    return False


# Check that DOT is a supported format
if not has_dot_library():
    for k in list(_graphformats.values()):
        try:
            k.remove('dot')
        except ValueError:
            pass

#################################################################
#          Graph reader/writer
#################################################################


def _process_graph_io_arguments(iofile, graph_type, file_format, multi_edges):
    """Test if the argument for the graph I/O functions make sense"""

    # Check the file
    if not isinstance(iofile, io.TextIOBase) and \
       not isinstance(iofile, io.IOBase) and \
       not isinstance(iofile, StringIO):
        raise ValueError(
            "The IO stream \"{}\" does not correspond to a file".format(
                iofile))

    # Check the graph type specification
    if graph_type not in _graphformats:
        raise ValueError("The graph type must be one of " +
                         list(_graphformats.keys()))

    elif graph_type in {"dag", "digraph"}:
        if multi_edges:
            grtype = networkx.MultiDiGraph
        else:
            grtype = networkx.DiGraph
    elif graph_type in {"simple", 'bipartite'}:
        if multi_edges:
            grtype = networkx.MultiGraph
        else:
            grtype = networkx.Graph
    else:
        raise RuntimeError(
            "Unchecked graph type argument: {}".format(graph_type))

    # Check/discover file format specification
    if file_format == 'autodetect':
        try:
            extension = os.path.splitext(iofile.name)[-1][1:]
        except AttributeError:
            raise ValueError(
                "Cannot guess a file format from an IO stream with no name. Please specify the format manually."
            )
        if extension not in _graphformats[graph_type]:
            raise ValueError("Cannot guess a file format for {} graphs from the extension of \"{}\". Please specify the format manually.".\
                             format(graph_type,iofile.name))
        else:
            file_format = extension

    elif file_format not in _graphformats[graph_type]:
        raise ValueError(
            "For {} graphs we only support these formats: {}".format(
                graph_type, _graphformats[graph_type]))

    return (grtype, file_format)


def readGraph(input_file,
              graph_type,
              file_format='autodetect',
              multi_edges=False):
    """Read a Graph from file

    The graph are managed using the NetworkX library, and most of the
    input and output formats are the ones supported by it. Plus we
    added support for some more *hackish* formats that are useful
    in applications.

    For the "simple" types, the graph is actually a (Multi)Graph
    object, while it is a (Multi)DiGraph in case of "dag" or
    "digraph".

    In the case of "dag" type, the graph is guaranteed to be acyclic
    and to pass the ``is_dag`` test. 

    In the case of "bipartite" type, the graph is of
    :py:class:`cnfgen.graphs.BaseBipartiteGraph`.


    Parameters
    -----------
    input_file: str or file-like object
        the input file from which the graph is read. If it is a string
        then the graph is read from a file with that string as
        filename. Otherwise if the input_file is a file object (or
        a text stream), the graph is read from there.

        Input files are assumed to be UTF-8 by default.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also :py:func:`cnfgen.graph.supported_formats`

    file_format: string, optional
        The file format that the parser should expect to receive.
        See also :py:func:`cnfgen.graph.supported_formats`. By default
        it tries to autodetect it from the file name extension (when applicable).

    multi_edges: bool,optional
        are multiple edge allowed in the graph? By default this is not allowed.

    Returns
    -------
    a graph object
        one among networkx.DiGraph, networkx.MultiDiGraph,
        networkx.Graph, networkx.MultiGraph object.

    Raises
    ------
    ValueError
        raised when either ``input_file`` is neither a file object
        nor a string, or when ``graph_type`` and ``file_format`` are
        invalid choices.

    IOError
        it is impossible to read the ``input_file``

    See Also
    --------
    writeGraph, is_dag

    """

    # file name instead of file object
    if isinstance(input_file, str):
        with open(input_file, 'r', encoding='utf-8') as file_handle:
            return readGraph(file_handle, graph_type, file_format, multi_edges)

    grtype, file_format = _process_graph_io_arguments(input_file, graph_type,
                                                      file_format, multi_edges)

    if file_format == 'dot':

        # This is a workaround. In theory a broken dot file should
        # cause a pyparsing.ParseError but the dot_reader used by
        # networkx seems to mismanage that and to cause a TypeError
        #
        try:
            G = grtype(networkx.nx_pydot.read_dot(input_file))
        except TypeError:
            raise ValueError('Parse Error in dot file')

    elif file_format == 'gml':

        # Networkx's GML reader expects to read from ascii encoded
        # binary file. We could have sent the data to a temporary
        # binary buffer but for some reasons networkx's GML reader
        # function is poorly written and does not like such buffers.
        # It turns out we can pass the data as a list of
        # encoded ascii lines.

        try:
            G = grtype(
                networkx.read_gml(line.encode('ascii') for line in input_file))
        except networkx.NetworkXError as errmsg:
            raise ValueError("[Parse error in GML input] {} ".format(errmsg))
        except UnicodeEncodeError as errmsg:
            raise ValueError(
                "[Non-ascii chars in GML file] {} ".format(errmsg))

    elif file_format == 'kthlist':

        G = _read_graph_kthlist_format(input_file,
                                       grtype,
                                       bipartition=(graph_type == 'bipartite'))

    elif file_format == 'dimacs':

        G = _read_graph_dimacs_format(input_file, grtype)

    elif file_format == 'matrix':

        G = _read_graph_matrix_format(input_file)

    else:
        raise RuntimeError(
            "[Internal error] Format {} not implemented".format(file_format))

    if graph_type == "dag" and not is_dag(G):
        raise ValueError("[Input error] Graph must be acyclic")

    if graph_type == "bipartite" and not has_bipartition(G):
        raise ValueError("[Input error] Graph must be bipartite")

    return G


def writeGraph(G, output_file, graph_type, file_format='autodetect'):
    """Write a graph to a file

    Parameters
    -----------
    G : networkx.Graph (or similar)

    output_file: file object
        the output file to which the graph is written. If it is a string
        then the graph is written to a file with that string as
        filename. Otherwise if ``output_file`` is a file object (or
        a text stream), the graph is written there.

        The file is written in UTF-8 by default.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also :py:func:`cnfgen.graph.supported_formats`

    file_format: string, optional
        The file format that the parser should expect to receive.
        See also :py:func:`cnfgen.graph.supported_formats`. By default
        it tries to autodetect it from the file name extension (when applicable).

    Returns
    -------
    None

    Raises
    ------
    ValueError
        raised when either ``output_file`` is neither a file object
        nor a string, or when ``graph_type`` and ``file_format`` are
        invalid choices.

    IOError
        it is impossible to write on the ``output_file``

    See Also
    --------
    readGraph

    """

    # file name instead of file object
    if isinstance(output_file, str):
        with open(output_file, 'w', encoding='utf-8') as file_handle:
            return writeGraph(G, file_handle, graph_type, file_format)

    _, file_format = _process_graph_io_arguments(output_file, graph_type,
                                                 file_format, False)

    if file_format == 'dot':

        networkx.nx_pydot.write_dot(G, output_file)

    elif file_format == 'gml':

        # Networkx's GML writer expects to write to an ascii encoded
        # binary file. Thus we need to let Networkx write to
        # a temporary binary ascii encoded buffer and then convert the
        # content before sending it to the output file.
        tempbuffer = io.BytesIO()
        networkx.write_gml(G, tempbuffer)
        print(tempbuffer.getvalue().decode('ascii'), file=output_file)

    elif file_format == 'kthlist' and graph_type != 'bipartite':

        _write_graph_kthlist_nonbipartite(G, output_file)

    elif file_format == 'kthlist' and graph_type == 'bipartite':

        _write_graph_kthlist_bipartite(G, output_file)

    elif file_format == 'dimacs':

        _write_graph_dimacs_format(G, output_file)

    elif file_format == 'matrix':

        _write_graph_matrix_format(G, output_file)

    else:
        raise RuntimeError(
            "[Internal error] Format {} not implemented".format(file_format))


#
# test for dag / with caching
#
def is_dag(digraph):
    """Test is a directed graph is acyclic

    if the input graph has a member `topologically_sorted' then assumed that
    there is a member `ordered_vertices' and that it is a topological order.

    Arguments:
    - `digraph`: input graph
    """

    if not isinstance(digraph, (networkx.MultiDiGraph, networkx.DiGraph)):
        return False

    elif hasattr(digraph, "topologically_sorted"):

        assert hasattr(digraph, "ordered_vertices")
        assert digraph.order() == len(digraph.ordered_vertices)
        assert set(digraph.nodes()) == set(digraph.ordered_vertices)
        assert networkx.algorithms.is_directed_acyclic_graph(digraph)
        return True

    else:
        return networkx.algorithms.is_directed_acyclic_graph(digraph)


#
# Use, when possible, a fixed vertex order
#
def enumerate_vertices(graph):
    """Return the ordered list of vertices of `graph`

    Parameters
    ----------
    graph : input graph
    """
    if hasattr(graph, "ordered_vertices"):
        assert graph.order() == len(graph.ordered_vertices)
        assert set(graph.nodes()) == set(graph.ordered_vertices)
        return graph.ordered_vertices
    else:
        setattr(graph, "ordered_vertices", sorted(graph.nodes()))
        return graph.ordered_vertices


def enumerate_edges(graph):
    """Return the ordered list of edges of `graph`

    Parameters
    ----------
    graph : input graph
    """
    if hasattr(graph, "ordered_edges"):
        assert set(graph.edges()) == set(graph.ordered_edges)
        return graph.ordered_edges
    else:
        setattr(graph, "ordered_edges", sorted(graph.edges()))
        return graph.ordered_edges


def neighbors(graph, v):
    """Return the ordered list of neighbors ov a vertex

    Parameters
    ----------
    graph : input graph

    v : vertex
    """
    return sorted(graph.neighbors(v))


#
# In-house parsers
#


# kth graph format reader
def _read_graph_kthlist_format(inputfile,
                               graph_class=networkx.DiGraph,
                               bipartition=False):
    """Read a graph from file, in the KTH reverse adjacency lists format.

    If the vertices are listed from to sources to the sinks, then the
    graph is marked as topologically sorted, and any DAG test will be
    answered without running any visit to the graph. Otherwise no
    assumption is made.

    If the file is supposed to represent a bipartite graph (i.e.
    when `bipartition` parameters is true) then each target node of an
    edge will be part of the left side and and each source node will
    be on the right side. Vertices that are never named are considered
    to be isolated vertices on the right side.

    Parameters
    ----------
    inputfile : file object
        file handle of the input

    graph_class: class object
        the graph class to read, one of networkx.DiGraph (default)
        networkx.MultiDiGraph networkx.Graph networkx.MultiGraph

    bipartition : boolean
        enforce that each edge (u,v) is such that u in in the left size

    Raises
    ------
    ValueError
        Error parsing the file
    """
    if graph_class not in [
            networkx.DiGraph, networkx.MultiDiGraph, networkx.Graph,
            networkx.MultiGraph
    ]:
        raise RuntimeError(
            "[Internal error] Attempt to use an unsupported class for graph representation."
        )

    G = graph_class()
    G.name = ''
    G.ordered_vertices = []

    # is the input topologically sorted?
    topologically_sorted_input = True

    # vertex number
    nvertex = -1
    vertex_cnt = -1

    for i, l in enumerate(inputfile.readlines()):

        # add the comment to the header
        if l[0] == 'c':
            G.name += l[2:]
            continue

        # empty line
        if len(l.strip()) == 0:
            continue

        if ':' not in l:
            # vertex number spec
            if nvertex >= 0:
                raise ValueError(
                    "Line {} contains a second spec directive.".format(i))
            try:
                nvertex = int(l.strip())
                if nvertex < 0:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    "Non negative number expected at line {}.".format(i))
            G.add_nodes_from(range(1, nvertex + 1))
            G.ordered_vertices = range(1, nvertex + 1)
            continue

        # Load edges from this line
        target, sources = l.split(':')
        try:
            target = int(target.strip())
            sources = [int(s) for s in sources.split()]
        except ValueError:
            raise ValueError("Non integer vertex ID at line {}.".format(i))
        if len(sources) < 1 or sources[-1] != 0:
            raise ValueError("Line {} must end with 0.".format(i))

        if target < 1 or target > nvertex:
            raise ValueError(
                "Vertex ID out of range [1,{}] at line {}.".format(nvertex, i))

        sources.pop()
        if len([x for x in sources if x < 1 or x > nvertex]) > 0:
            raise ValueError(
                "Vertex ID out of range [1,{}] at line {}.".format(nvertex, i))

        # Vertices should appear in increasing order if the graph is topologically sorted
        for s in sources:
            if s <= target:
                topologically_sorted_input = False

        # Check the bi-coloring on both side
        if bipartition:
            colors = [
                G.nodes[s]['bipartite'] for s in sources
                if 'bipartite' in G.nodes[s]
            ]

            if 'bipartite' in G.nodes[target]:
                colors += [1 - G.nodes[target]['bipartite']]

            if len(set(colors)) > 1:
                raise ValueError(
                    "Greedy bicoloring incompatible with edges in line {}.".
                    format(i))

            default_color = 0 if len(colors) == 0 else 1 - colors[0]
            G.nodes[target]['bipartite'] = default_color
            for s in sources:
                G.nodes[s]['bipartite'] = 1 - default_color

        # after vertices, add the edges
        for s in sources:
            G.add_edge(s, target)

    # label the bipartition on residual vertices
    if bipartition:
        for v in G.ordered_vertices:
            if 'bipartite' not in G.nodes[v]:
                G.nodes[v]['bipartite'] = 1

    # cache the information that the graph is topologically sorted.
    if topologically_sorted_input:
        G.topologically_sorted = True

    if nvertex != G.order():
        raise ValueError("{} vertices expected. Got {} instead.".format(
            nvertex, G.order()))

    if bipartition:
        return BipartiteGraph.from_networkx(G)
    else:
        return G


def _read_graph_dimacs_format(inputfile, graph_class=networkx.Graph):
    """Read a graph simple from file, in the DIMACS edge format.

    Parameters
    ----------
    inputfile : file object
        file handle of the input

    graph_class: class object
        the graph class to read, one of networkx.DiGraph (default)
        networkx.MultiDiGraph networkx.Graph networkx.MultiGraph
    """
    if not graph_class in [
            networkx.Graph, networkx.MultiGraph, networkx.DiGraph,
            networkx.MultiDiGraph
    ]:
        raise ValueError(
            "[Internal error] Attempt to use an unsupported class for graph representation."
        )

    G = graph_class()
    G.name = ''

    n = -1
    m = -1
    m_cnt = 0

    # is the input topologically sorted?
    for i, l in enumerate(inputfile.readlines()):

        # add the comment to the header
        if l[0] == 'c':
            G.name += l[2:]
            continue

        # parse spec line
        if l[0] == 'p':
            if n >= 0:
                raise ValueError(
                    "[Syntax error] " +
                    "Line {} contains a second spec line.".format(i))
            _, fmt, nstr, mstr = l.split()
            if fmt != 'edge':
                raise ValueError("[Input error] " +
                                 "Dimacs \'edge\' format expected.")
            n = int(nstr)
            m = int(mstr)
            G.add_nodes_from(range(1, n + 1))
            continue

        # parse spec line
        if l[0] == 'e':
            m_cnt += 1
            _, v, w = l.split()
            G.add_edge(int(v), int(w))

    if m != m_cnt:
        raise ValueError("[Syntax error] " +
                         "{} edges were expected.".format(m))

    return G


def _read_graph_matrix_format(inputfile):
    """Read a bipartite graph from file, in the adjiacency matrix format.

    This is an example of an adjacency matrix for a bipartite graph
    with 9 vertices on one side and 15 on the another side.

    .. 9 15
       1 1 0 1 0 0 0 1 0 0 0 0 0 0 0
       0 1 1 0 1 0 0 0 1 0 0 0 0 0 0
       0 0 1 1 0 1 0 0 0 1 0 0 0 0 0
       0 0 0 1 1 0 1 0 0 0 1 0 0 0 0
       0 0 0 0 1 1 0 1 0 0 0 1 0 0 0
       0 0 0 0 0 1 1 0 1 0 0 0 1 0 0
       0 0 0 0 0 0 1 1 0 1 0 0 0 1 0
       0 0 0 0 0 0 0 1 1 0 1 0 0 0 1
       1 0 0 0 0 0 0 0 1 1 0 1 0 0 0

    Parameters
    ----------
    inputfile: file object
        the file containing the graph specification

    Returns
    -------
    G : BipartiteGraph

    """
    def scan_integer(inputfile):

        num_buffer = []
        line_cnt = 0

        while True:
            if len(num_buffer) == 0:

                line = inputfile.readline()

                if len(line) == 0:
                    return

                line_cnt += 1
                tokens = line.split()

                if len(tokens) == 0 or tokens[0][0] == '#':
                    continue  # comment line

                try:
                    num_buffer.extend((int(lit), line_cnt) for lit in tokens)
                except ValueError:
                    raise ValueError("[Syntax error] " +
                                     "Line {} contains a non numeric entry.".
                                     format(line_cnt))

            yield num_buffer.pop(0)

    scanner = scan_integer(inputfile)

    try:
        n = next(scanner)[0]
        m = next(scanner)[0]

        G = BipartiteGraph(n, m)
        G.name = ''

        # read edges
        for i in range(1, n + 1):
            for j in range(1, m + 1):

                (b, l) = next(scanner)
                if b == 1:
                    G.add_edge(i, j)
                elif b == 0:
                    pass
                else:
                    raise ValueError(
                        "[Input error at line {}] Only 0 or 1 are allowed".
                        format(l))
    except StopIteration:
        raise ValueError("[Input error] Unexpected end of the matrix")

    # check that there are is no more data
    try:
        (b, l) = next(scanner)
        raise ValueError(
            "[Input error at line {}] There are more than {}x{} entries".
            format(l, n, m))
    except StopIteration:
        pass

    return G


#
# In-house graph writers
#
def _write_graph_kthlist_nonbipartite(G, output_file):
    """Wrire a graph to a file, in the KTH reverse adjacency lists format.

    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """
    print("c {}".format(G.name), file=output_file)
    print("{}".format(G.order()), file=output_file)

    # we need numerical indices for the vertices
    # adj list in the same order
    indices = {v: i for (i, v) in enumerate(enumerate_vertices(G), start=1)}

    V = enumerate_vertices(G)

    from io import StringIO
    output = StringIO()

    for v in V:

        if G.is_directed():
            nbors = [indices[w] for w in G.predecessors(v)]
        else:
            nbors = [indices[w] for w in G.adj[v].keys()]

        nbors.sort()

        output.write(str(indices[v]) + " : ")
        output.write(" ".join([str(i) for i in nbors]))
        output.write(" 0\n")

    print(output.getvalue(), file=output_file)


def _write_graph_kthlist_bipartite(G, output_file):
    """Wrire a bipartite graph to a file, 
       in the KTH reverse adjacency lists format.

    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    print("c {}".format(G.name), file=output_file)
    print("{}".format(G.order()), file=output_file)

    from io import StringIO
    output = StringIO()

    U, _ = G.parts()
    offset = len(U)

    for u in U:
        output.write(str(u) + " : ")
        output.write(" ".join([str(v + offset) for v in G.right_neighbors(u)]))
        output.write(" 0\n")

    print(output.getvalue(), file=output_file)


def _write_graph_dimacs_format(G, output_file):
    """Wrire a graph to a file, in DIMACS format.

    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    print("c {}".format(G.name).strip(), file=output_file)
    vertices = dict((name, index) for index, name in enumerate(G.nodes(), 1))
    edges = G.edges()
    print("p edge {} {}".format(len(vertices), len(edges)), file=output_file)

    for v, w in edges:
        print("e {} {}".format(vertices[v], vertices[w]), file=output_file)


def _write_graph_matrix_format(G, output_file):
    """Wrire a graph to a file, in \"matrix\" format.

    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    print("{} {}".format(len(G.left_order()), len(G.right_order())),
          file=output_file)
    L, R = G.parts()
    for u in L:

        adj_row = []

        for v in R:
            if G.has_edge(u, v):
                adj_row.append("1")
            else:
                adj_row.append("0")

        print(" ".join(adj_row), file=output_file)


#
# Bipartite graph generator
# (we do not want to use networkx)
#
def bipartite_random_left_regular(l, r, d, seed=None):
    """Returns a random bipartite graph with constant left degree.

    Each vertex on the left side has `d` neighbors on the right side,
    picked uniformly at random without repetition.

    Each vertex in the graph has an attribute `bipartite` which is 0
    for the vertices on the left side and 1 for the vertices on the
    right side.

    Parameters
    ----------
    l : int
        vertices on the left side
    r : int
        vertices on the right side
    d : int
        degree on the left side.
    seed : hashable object
        seed the random generator

    Returns
    -------
    networkx.Graph

    Raises
    ------
    ValueError
        unless ``l``, ``r`` and ``d`` are non negative.

    """
    import random
    if seed is not None:
        random.seed(seed)

    if l < 0 or r < 0 or d < 0:
        raise ValueError(
            "bipartite_random_left_regular(l,r,d) needs l,r,d >=0.")

    G = BipartiteGraph(l, r)
    G.name = "bipartite_random_left_regular({},{},{})".format(l, r, d)
    d = min(r, d)

    L, R = G.parts()
    for u in L:
        for v in sorted(random.sample(R, d)):
            G.add_edge(u, v)

    return G


def bipartite_random_m_edges(L, R, m, seed=None):
    """Returns a random bipartite graph with M edges

    Build a random bipartite graph with :math:`L` left vertices,
    :math:`R` right vertices and :math:`m` edges sampled at random
    without repetition.

    Parameters
    ----------
    L : int
        vertices on the left side
    R : int
        vertices on the right side
    m : int
        number of edges.
    seed : hashable object
        seed the random generator

    Returns
    -------
    BipartiteGraph

    Raises
    ------
    ValueError
        unless ``L``, ``R`` and ``m`` are non negative.

    """
    import random
    if seed is not None:
        random.seed(seed)

    if L < 1 or R < 1 or m < 0 or m > L * R:
        raise ValueError(
            "bipartite_random_m_edges(L,R,m) needs L, R >= 1, 0<=m<=L*R")
    G = BipartiteGraph(L, R)
    G.name = "bipartite_random_m_edges({},{},{})".format(L, R, m)

    U, V = G.parts()

    if m > L * R // 3:
        # Sampling strategy (dense)
        E = ((u, v) for u in U for v in V)
        for u, v in random.sample(E, m):
            G.add_edge(u, v)
    else:
        # Sampling strategy (sparse)
        count = 0
        while count < m:
            u = random.randint(1, L)
            v = random.randint(1, R)
            if not G.has_edge(u, v):
                G.add_edge(u, v)
                count += 1
    assert G.size() == m
    return G


def bipartite_random(L, R, p, seed=None):
    """Returns a random bipartite graph with independent edges

    Build a random bipartite graph with :math:`L` left vertices,
    :math:`R` right vertices, where each edge is sampled independently
    with probability :math:`p`.

    Parameters
    ----------
    L : int
        vertices on the left side
    R : int
        vertices on the right side
    p : float
        probability to pick an edge
    seed : hashable object
        seed the random generator

    Returns
    -------
    BipartiteGraph

    Raises
    ------
    ValueError
        unless ``L``, ``R`` are non negative and 0<=``p``<=1.
    """
    import random
    if seed is not None:
        random.seed(seed)

    if L < 1 or R < 1 or p < 0 or p > 1:
        raise ValueError(
            "bipartite_random_graph(L,R,p) needs L, R >= 1, p in [0,1]")
    G = BipartiteGraph(L, R)
    G.name = "bipartite_random_graph({},{},{})".format(L, R, p)

    U, V = G.parts()

    for u in U:
        for v in V:
            if random.random() <= p:
                G.add_edge(u, v)
    return G


def bipartite_shift(N, M, pattern=[]):
    """Returns a bipartite graph where edges are a fixed shifted sequence.

    The graph has :math:`N` vertices on the left (numbered from
    :math:`1` to :math:`N`), and :math:`M` vertices on the right
    (numbered from :math:`1` to :math:`M`),

    Each vertex :math:`v` on the left side has edges to vertices
    :math:`v+d_1`, :math:`v+d_2`, :math:`v+d_3`,... with vertex
    indices on the right wrap around :wrap around over
    :math:`[1..M]`).

    Notice that this construction does not produces multiedges even if
    two offsets end up on the same right vertex.

    Parameters
    ----------
    N : int
        vertices on the left side
    M : int
        vertices on the right side
    pattern : list(int)
        pattern of neighbors

    Returns
    -------
    BipartiteGraph

    Raises
    ------
    ValueError
        unless ``N``, ``M`` are non negative and ``pattern`` has vertices outside the range.

    """
    if N < 1 or M < 1:
        raise ValueError("bipartite_shift(N,M,pattern) needs N,M >= 0.")

    G = BipartiteGraph(N, M)
    G.name = "bipartite_shift_regular({},{},{})".format(N, M, pattern)

    L, R = G.parts()
    pattern.sort()
    for u in L:
        for offset in pattern:
            G.add_edge(u, 1 + (u - 1 + offset) % M)

    return G


def bipartite_random_regular(l, r, d, seed=None):
    """Returns a random bipartite graph with constant degree on both sides.

    The graph is d-regular on the left side and regular on the right
    size, so it must be that d*l / r is an integer number.

    Parameters
    ----------
    l : int
       vertices on the left side
    r : int
       vertices on the right side
    d : int
       degree of vertices at the left side
    seed : hashable object
       seed of random generator

    Returns
    -------
    networkx.Graph

    Raises
    ------
    ValueError
        if one among ``l``, ``r`` and ``d`` is negative or
        if ``r`` does not divides `l*d`

    References
    ----------
    [1] http://...

    """

    import random
    if seed is not None:
        random.seed(seed)

    if l < 0 or r < 0 or d < 0:
        raise ValueError("bipartite_random_regular(l,r,d) needs l,r,d >=0.")

    if (l * d) % r != 0:
        raise ValueError(
            "bipartite_random_regular(l,r,d) needs r to divid l*d.")

    G = BipartiteGraph(l, r)
    G.name = "bipartite_random_regular({},{},{})".format(l, r, d)

    L, R = G.parts()
    A = list(L) * d
    B = list(R) * (l * d // r)
    assert len(B) == l * d

    for i in range(l * d):
        # Sample an edge, do not add it if it existed
        # We expect to sample at most d^2 edges
        for retries in range(3 * d * d):
            ea = random.randint(i, l * d - 1)
            eb = random.randint(i, l * d - 1)
            if not G.has_edge(A[ea], B[eb]):
                G.add_edge(A[ea], B[eb])
                A[i], A[ea] = A[ea], A[i]
                B[i], B[eb] = B[eb], B[i]
                break
        else:
            # Sampling takes too long, maybe no good edge exists
            failure = True
            for ea in range(i, l * d):
                for eb in range(i, l * d):
                    if not G.has_edge(A[ea], B[eb]):
                        failure = False
                        break
                if not failure:
                    break
            if failure:
                return bipartite_random_regular(l, r, d)

    return G


def dag_pyramid(height):
    """Generates the pyramid DAG

    Parameters
    ----------
    height : int
        the height of the tree

    Returns
    -------
    networkx.DiGraph
    """
    D = networkx.DiGraph()
    D.name = 'Pyramid of height {}'.format(height)
    D.ordered_vertices = []

    # vertices
    X=[ [('x_{{{},{}}}'.format(h,i),h,i) for i in range(height-h+1)] \
        for h in range(height+1) ]

    for layer in X:
        for (name, h, i) in layer:
            D.add_node(name, rank=(h, i))
            D.ordered_vertices.append(name)

    # edges
    for h in range(1, len(X)):
        for i in range(len(X[h])):
            D.add_edge(X[h - 1][i][0], X[h][i][0])
            D.add_edge(X[h - 1][i + 1][0], X[h][i][0])

    return D


def dag_complete_binary_tree(height):
    """Generates the complete binary tree DAG

    Parameters
    ----------
    height : int
        the height of the tree

    Returns
    -------
    networkx.DiGraph
    """
    D = networkx.DiGraph()
    D.name = 'Complete binary tree of height {}'.format(height)
    D.ordered_vertices = []
    # vertices
    vert = ['v_{}'.format(i) for i in range(1, 2 * (2**height))]
    for w in vert:
        D.add_node(w)
        D.ordered_vertices.append(w)
    # edges
    N = len(vert) - 1
    for i in range(len(vert) // 2):
        D.add_edge(vert[N - 2 * i - 1], vert[N - i])
        D.add_edge(vert[N - 2 * i - 2], vert[N - i])

    return D


def dag_path(length):
    """Generates a directed path DAG

    Parameters
    ----------
    length : int
        the length of the path

    Returns
    -------
    networkx.DiGraph
    """
    D = networkx.DiGraph()
    D.name = 'Directed path of length {}'.format(length)
    D.ordered_vertices = []
    # vertices
    V = ['v_{}'.format(i) for i in range(0, length + 1)]
    for v in V:
        D.add_node(v)
        D.ordered_vertices.append(v)
    # edges
    for i in range(len(V) - 1):
        D.add_edge(V[i], V[i + 1])

    return D


def sample_missing_edges(G, m, seed=None):
    """Sample m pairs of missing edges in G

    If :math:`G` is not complete and has at least :math:`m` missing edges, :math:`m` of them are sampled.

    Parameters
    ----------
    G : networkx.Graph
        a graph with at least :math:`m` missing edges
    m : int
       the number of missing edges to sample
    seed : hashable object
       seed of random generator

    Returns
    -------
    list of edges

    Raises
    ------
    ValueError
        if :math:`G` doesn't have :math:`m` missing edges
    RuntimeError
        Sampling failure in the sparse case


    """

    import random
    if seed is not None:
        random.seed(seed)

    from networkx import non_edges

    if m < 0:
        raise ValueError("You can only sample a non negative number of edges.")

    total_number_of_edges = None

    if has_bipartition(G):

        Left, Right = G.parts()
        total_number_of_edges = len(Left) * len(Right)

        def edge_sampler():
            u = random.sample(Left, 1)[0]
            v = random.sample(Right, 1)[0]
            return (u, v)

        def available_edges():
            return [(u, v) for u in Left for v in Right
                    if not G.has_edge(u, v)]

    else:

        total_number_of_edges = G.order() * (G.order() - 1) / 2

        def edge_sampler():
            return random.sample(G.nodes(), 2)

        def available_edges():
            return list(non_edges(G))

    number_avaiable_edges = total_number_of_edges - G.number_of_edges()

    if number_avaiable_edges < m:
        raise ValueError(
            "The graph does not have {} missing edges to sample.".format(m))

    if G.number_of_edges() + m >= total_number_of_edges / 2:
        # Large density case: enumerate missing edges and sample.
        return random.sample(available_edges(), m)

    else:
        # Sparse case: sample and retry
        sampled_edges = set()
        addition = []

        for _ in range(100 * m):

            if len(addition) >= m:
                break

            u, v = edge_sampler()
            if (u,v) not in sampled_edges and \
               (v,u) not in sampled_edges and \
               not G.has_edge(u,v):
                addition.append((u, v))
                sampled_edges.add((u, v))

        if len(addition) >= m:
            return addition
        else:
            raise RuntimeError(
                "Improbable failure at sampling missing edges in a sparse graph."
            )
