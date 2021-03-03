#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to manage graph formats and graph files in order to build
formulas that are graph based.
"""

import networkx
import os
import io
from io import StringIO
import copy
from bisect import bisect_right
__all__ = [
    "supported_formats", "readGraph", "writeGraph", "is_dag",
    "enumerate_vertices", "enumerate_edges", "neighbors",
    "bipartite_random_left_regular", "bipartite_random_regular",
    "bipartite_random_m_edges", "bipartite_random", "dag_complete_binary_tree",
    "dag_pyramid",'BipartiteGraph', 'Graph'
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


class BipartiteEdgeList():
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


class BaseGraph():
    """Base class for graphs"""

    def is_dag(self):
        """Test whether the graph is directed acyclic

This is not a full test. It only checks that all directed edges (u,v)
have that u < v."""
        raise NotImplementedError

    def is_directed(self):
        "Test whether the graph is directed"
        raise NotImplementedError

    def is_multigraph(self):
        "Test whether the graph can have multi-edges"
        return False

    def is_bipartite(self):
        "Test whether the graph is a bipartite object"
        return isinstance(self, BaseBipartiteGraph)

    def order(self):
        raise NotImplementedError

    def size(self):
        return len(self.edges())

    def number_of_edges(self):
        return self.size()

    def has_edge(self, u, v):
        raise NotImplementedError

    def add_edge(self, u, v):
        raise NotImplementedError

    def add_edges_from(self, edges):
        for u, v in edges:
            self.add_edge(u, v)

    def edges(self):
        raise NotImplementedError

    def __len__(self):
        return self.order()

    def to_networkx(self):
        """Convert the graph TO a networkx object."""
        raise NotImplementedError

class Graph(networkx.Graph, BaseGraph):

    def is_dag(self):
        return False
    def is_directed(self):
        return False

    def __init__(self,n):
        if n<0:
            raise ValueError("n must be non negative")
        networkx.Graph.__init__(self)
        self.n = n
        if n>0:
            self.add_nodes_from(range(1,n+1))

    def add_edge(self,u,v):
        if not (1 <= u <= self.n and 1 <= v <= self.n and u!=v):
            raise ValueError("u,v must be distinct, between 1 and the number of nodes")
        networkx.Graph.add_edge(self,u,v)

    def has_edge(self,u,v):
        return networkx.Graph.has_edge(self,u,v)

    def to_networkx(self):
        return self

    def neighbors(self,v):
        yield from networkx.Graph.neighbors(self,v)

    @classmethod
    def from_networkx(cls, G):
        G = normalize_networkx_labels(G)
        C = cls(G.order())
        C.add_edges_from(G.edges())
        try:
            C.name= G.name
        except AttributeError:
            pass
        return C

    @classmethod
    def null_graph(cls):
        G = cls(0)
        G.name = 'null graph'
        return G

    @classmethod
    def empty_graph(cls,n):
        G = cls(n)
        G.name = 'empty graph of order '+str(n)
        return G

    @classmethod
    def complete_graph(cls,n):
        G = cls(n)
        for u in range(1,n):
            for v in range(u+1,n+1):
                G.add_edge(u,v)
        G.name = 'complete graph of order '+str(n)
        return G

class BaseBipartiteGraph(BaseGraph):
    """Base class for bipartite graphs"""

    def __init__(self, L, R):
        if L < 0 or R < 0:
            raise ValueError(
                "Left and right size of the bipartite graph must be non-negative"
            )
        self.lorder = L
        self.rorder = R
        self.name = 'Bipartite graph with ({},{}) vertices'.format(L, R)

    def is_bipartite(self):
        return True

    def order(self):
        return self.lorder + self.rorder

    def edges(self):
        return BipartiteEdgeList(self)

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

    def to_networkx(self):
        G = networkx.Graph()
        n, m = self.lorder, self.rorder
        G.add_nodes_from(range(1, n+1), bipartite=0)
        G.add_nodes_from(range(n+1, m+n+1), bipartite=1)
        G.add_edges_from((u, v+n) for (u, v) in self.edges())
        return G


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

        - multi-edges are not allowed
        - neighbors of a vertex are kept in numberic order

        Examples
        --------
        >>> G = BipartiteGraph(3,5)
        >>> G.add_edge(2,3)
        >>> G.add_edge(2,2)
        >>> G.add_edge(2,3)
        >>> G.right_neighbors(2)
        [2, 3]
        """
        if not (1 <= u <= self.lorder and 1 <= v <= self.rorder):
            raise ValueError("Invalid choice of vertices")

        if self.has_edge(u, v):
            return

        if u not in self.ladj:
            self.ladj[u] = []
        if v not in self.radj:
            self.radj[v] = []

        pv = bisect_right(self.ladj[u], v)
        pu = bisect_right(self.radj[v], u)
        self.ladj[u].insert(pv, v)
        self.radj[v].insert(pu, u)
        self.edgecount += 1

    def right_neighbors(self, u):
        if not (1 <= u <= self.lorder):
            raise ValueError("Invalid choice of vertex")
        return self.ladj.get(u, [])[:]

    def left_neighbors(self, v):
        if not (1 <= v <= self.rorder):
            raise ValueError("Invalid choice of vertex")
        return self.radj.get(v, [])[:]

    @classmethod
    def from_networkx(cls, G):
        """Convert a :py:class:`networkx.Graph` into a :py:class:`cnfgen.graphs.BipartiteGraph`

        In order to convert a :py:class:`networkx.Graph` object `G`,
        it is necessary that all nodes in `G` have the property
        `bipartite` set to either `0` or `1`.

        If this is not the case, or if there are edges between the two
        parts, :py:class:`ValueError` is raised.

        Example
        -------
        >>> G = networkx.bipartite.complete_bipartite_graph(5,7)
        >>> B = BipartiteGraph.from_networkx(G)
        >>> print(B.order())
        12
        >>> print(B.left_order())
        5
        >>> print(B.has_edge(2,3))
        True
        """
        side = [[], []]
        index = [{}, {}]
        for u in G.nodes():
            try:
                color = G.nodes[u]['bipartite']
                assert color in ['0', 0, '1', 1]
            except (KeyError, AssertionError):
                raise ValueError(
                    "Node {} lacks the 'bipartite' property set to 0 or 1".format(u))
            side[int(color)].append(u)

        B = cls(len(side[0]), len(side[1]))
        index[0] = {u: i for (i, u) in enumerate(side[0], start=1)}
        index[1] = {v: i for (i, v) in enumerate(side[1], start=1)}
        for u, v in G.edges():
            ucolor = 0 if (u in index[0]) else 1
            vcolor = 1 if (v in index[1]) else 0

            if ucolor == vcolor:
                raise ValueError(
                    "Edge ({},{}) across the bipartition".format(u, v))

            iu, iv = index[ucolor][u], index[vcolor][v]
            if ucolor == 0:
                B.add_edge(iu, iv)
            else:
                B.add_edge(iv, iu)
        return B

    @classmethod
    def from_file(cls, fileorname, fileformat=None, multigraph=False):
        """Load the graph from a file

        The file format is either indicated in the `fileformat` variable or, if
        that is `None`, or from the extension of the filename.

        Parameters
        -----------
        fileorname: str or file-like object
            the input file from which the graph is read. If it is a string
            then the graph is read from a file with that string as
            filename. Otherwise if the fileorname is a file object (or
            a text stream), the graph is read from there.

            Input files are assumed to be UTF-8 by default.

        fileformat: string, optional
            The file format that the parser should expect to receive.
            See also :py:func:`cnfgen.graph.supported_formats`. By default
            it tries to autodetect it from the file name extension (when applicable).

        multi_edges: bool,optional
            are multiple edge allowed in the graph? By default this is not allowed."""

        # Reduce to the case of filestream
        if isinstance(fileorname,str):
            with open(fileorname, 'r', encoding='utf-8') as file_handle:
                return cls.from_file(fileorname,fileformat,multigraph)

        # Discover and test file format
        fileformat = guess_fileformat(fileorname, fileformat)
        if fileformat not in _graphformats['bipartite']:
            raise ValueError(
                "Invalid file type."
                " For bipartite graphs we support {}".format(_graphformats['bipartite']))

        # Read file
        return readGraph(fileorname,'bipartite',fileformat)




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


def guess_fileformat(fileorname, fileformat=None):
    """Guess the file format for the file or filename """
    if fileformat is not None:
        return fileformat

    try:
        if isinstance(fileorname, str):
            name = fileorname
        else:
            name = fileorname.name
        return os.path.splitext(name)[-1][1:]
    except (AttributeError, ValueError, IndexError):
        raise ValueError(
            "Cannot guess a file format from arguments. Please specify the format manually.")


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
            raise ValueError("Cannot guess a file format for {} graphs from the extension of \"{}\". Please specify the format manually.".
                             format(graph_type, iofile.name))
        else:
            file_format = extension

    elif file_format not in _graphformats[graph_type]:
        raise ValueError(
            "For {} graphs we only support these formats: {}".format(
                graph_type, _graphformats[graph_type]))

    return (grtype, file_format)


def normalize_networkx_labels(G):
    """Relabel all vertices as integer starting from 1"""
    # Normalize GML file. All nodes are integers starting from 1
    try:
        G = networkx.convert_node_labels_to_integers(
            G, first_label=1, ordering='sorted')
    except TypeError:
        # Ids cannot be sorted natively
        G = networkx.convert_node_labels_to_integers(
            G, first_label=1, ordering='default')
    return G


def readGraph(input_file,
              graph_type,
              file_format='autodetect',
              multi_edges=False):
    """Read a Graph from file

    In the case of "bipartite" type, the graph is of
    :py:class:`cnfgen.graphs.BaseBipartiteGraph`.

    Otherwise the graph is managed using the
    :pyclass:`networkx.Graph`. For the "simple" types, the graph is
    actually a (Multi)Graph object, while it is a (Multi)DiGraph in
    case of "dag" or "digraph".

    The supported file formats are enumearated by
    :py:func:`cnfgen.graph.supported_formats`

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
        one type among networkx.DiGraph, networkx.MultiDiGraph,
        networkx.Graph, networkx.MultiGraph, cnfgen.graphs.BipartiteGraph.

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
    writeGraph, is_dag, has_bipartition
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
            G = normalize_networkx_labels(G)
        except TypeError:
            raise ValueError('Parse Error in dot file')

    elif file_format == 'gml':

        # Networkx's GML reader expects to read from ascii encoded
        # binary file. We could have sent the data to a temporary
        # binary buffer but for some reasons networkx's GML reader
        # function is poorly written and does not like such buffers.
        # It turns out we can pass the data as a list of
        # encoded ascii lines.
        #
        # The 'id' field in the vertices are supposed to be an integer
        # and will be used as identifiers for the vertices in Graph
        # object too.
        #
        try:
            G = grtype(
                networkx.read_gml(
                    (line.encode('ascii') for line in input_file), label='id'))
            G = normalize_networkx_labels(G)
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
        try:
            G = BipartiteGraph.from_networkx(G)
        except ValueError:
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

        if has_bipartition(G):
            G = G.to_networkx()

        networkx.nx_pydot.write_dot(G, output_file)

    elif file_format == 'gml':

        # Networkx's GML writer expects to write to an ascii encoded
        # binary file. Thus we need to let Networkx write to
        # a temporary binary ascii encoded buffer and then convert the
        # content before sending it to the output file.
        tempbuffer = io.BytesIO()
        if has_bipartition(G):
            G = G.to_networkx()
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

    try:
        setattr(graph, "ordered_vertices", sorted(graph.nodes()))
        return graph.ordered_vertices
    except TypeError:
        # cannot sort the vertices
        return graph.nodes()


def enumerate_edges(graph):
    """Return the ordered list of edges of `graph`

    Parameters
    ----------
    graph : input graph
    """
    if hasattr(graph, "ordered_edges"):
        assert set(graph.edges()) == set(graph.ordered_edges)
        return graph.ordered_edges

    try:
        setattr(graph, "ordered_edges", sorted(graph.edges()))
        return graph.ordered_edges
    except TypeError:
        # could not sort the edges
        return graph.edges()


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
def _kthlist_parse(inputfile):
    """Read a graph from file, and produce the datas.

    First yeild (#vertex,first comment line)
    Then generates a sequence of (s,target,lineno)

    Raises:
        ValueError is parsing fails for some reason
    """
    # vertex number
    size = -1
    name = ""

    for i, l in enumerate(inputfile.readlines()):

        # first non empty comment line is the graph name
        # must be before the graph size
        if l[0] == 'c':
            if size < 0 and len(name) == 0 and len(l[2:].strip()) != 0:
                name += l[2:]
            continue

        # empty line
        if len(l.strip()) == 0:
            continue

        if ':' not in l:
            # vertex number spec
            if size >= 0:
                raise ValueError(
                    "Line {} contains a second spec directive.".format(i))
            try:
                size = int(l.strip())
                if size < 0:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    "Non negative number expected at line {}.".format(i))
            yield (size, name)
            continue

        # Load edges from this line
        left, right = l.split(':')
        try:
            left = int(left.strip())
            right = [int(s) for s in right.split()]
        except ValueError:
            raise ValueError("Non integer vertex ID at line {}.".format(i))
        if len(right) < 1 or right[-1] != 0:
            raise ValueError("Line {} must end with 0.".format(i))

        if left < 1 or left > size:
            raise ValueError(
                "Vertex ID out of range [1,{}] at line {}.".format(size, i))

        right.pop()
        if len([x for x in right if x < 1 or x > size]) > 0:
            raise ValueError(
                "Vertex ID out of range [1,{}] at line {}.".format(size, i))
        yield left, right, i


# kth graph format reader
def _read_graph_kthlist_format(inputfile,
                               graph_class=networkx.DiGraph,
                               bipartition=False):
    """Read a graph from file, in the KTH reverse adjacency lists format.

    Assumes the adjacecy list is given in order.
    - vertices are listed in increasing order
    - if directed graph the adjacency list specifies incoming neighbous
    - if DAG, the graph must be given in topological order source->sink
    - if bipartite, only the adjiacency list of the lft side must be
      given, no list for a vertex of the right side is allowed.

    Parameters
    ----------
    inputfile : file object
        file handle of the input

    graph_class: class object
        the graph class to read, one of networkx.DiGraph (default)
        networkx.MultiDiGraph networkx.Graph networkx.MultiGraph

    bipartition : boolean
        enforce reading a bipartite graph

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
    size = -1

    parser = _kthlist_parse(inputfile)

    size, name = next(parser)
    G.add_nodes_from(range(1, size + 1))
    G.ordered_vertices = range(1, size + 1)

    bipartition_ambiguous = [1, size]

    for left, right, lineno in parser:

        # Vertices should appear in increasing order if the graph is topologically sorted
        for v in right:
            if v <= left:
                topologically_sorted_input = False

        # Check the bi-coloring on both side
        if bipartition:
            if left > bipartition_ambiguous[1]:
                raise ValueError(
                    "Bipartition violation al line {}. Vertex {} cannot be on the left side."
                    .format(lineno, left))
            bipartition_ambiguous[0] = max(bipartition_ambiguous[0], left + 1)
            for v in right:
                if v < bipartition_ambiguous[0]:
                    raise ValueError(
                        "Bipartition violation. Invalid edge ({},{}) at line {}."
                        .format(left, v, lineno))
                bipartition_ambiguous[1] = min(bipartition_ambiguous[1], v - 1)

        # after vertices, add the edges
        for v in right:
            G.add_edge(left, v)

    # label the bipartition on residual vertices
    if bipartition:
        for i in range(1, bipartition_ambiguous[0]):
            G.nodes[i]['bipartite'] = 0
        for i in range(bipartition_ambiguous[0], size + 1):
            G.nodes[i]['bipartite'] = 1

    # cache the information that the graph is topologically sorted.
    if topologically_sorted_input:
        G.topologically_sorted = True

    if size != G.order():
        raise ValueError("{} vertices expected. Got {} instead.".format(
            size, G.order()))

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

    print("{} {}".format(G.left_order(), G.right_order()),
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

    Vertices are indexed from the bottom layer, starting from index 1

    Parameters
    ----------
    height : int
        the height of the pyramid graph (>=0)

    Returns
    -------
    networkx.DiGraph

    Raises
    ------
    ValueError
    """
    if height < 0:
        raise ValueError("The height of the tree must be >= 0")

    D = networkx.DiGraph()
    D.name = 'Pyramid of height {}'.format(height)

    # vertices
    vidx = 1
    for layer in range(height+1):
        for i in range(1, height-layer+2):
            D.add_node(vidx, rank=(layer, i),
                       label="X[{},{}]".format(layer, 1))
            vidx += 1

    # edges
    leftsrc = 1
    dest = height+2
    for layer in range(1, height+1):
        for i in range(1, height-layer+2):
            D.add_edge(leftsrc, dest)
            D.add_edge(leftsrc+1, dest)
            leftsrc += 1
            dest += 1
        leftsrc += 1

    return D


def dag_complete_binary_tree(height):
    """Generates the complete binary tree DAG

    Vertices are indexed from the bottom layer, starting from index 1

    Parameters
    ----------
    height : int
        the height of the tree

    Returns
    -------
    networkx.DiGraph

    Raises
    ------
    ValueError

    """
    if height < 0:
        raise ValueError("The height of the tree must be >= 0")

    D = networkx.DiGraph()
    D.name = 'Complete binary tree of height {}'.format(height)

    # vertices plus 1
    N = 2 * (2**height)
    D.add_nodes_from(range(1, N))
    # edges
    leftsrc = 1
    for dest in range(N // 2 + 1, N):
        D.add_edge(leftsrc, dest)
        D.add_edge(leftsrc+1, dest)
        leftsrc += 2

    return D


def dag_path(length):
    """Generates a directed path DAG

    Vertices are indexed from 1..length+1

    Parameters
    ----------
    length : int
        the length of the path

    Returns
    -------
    networkx.DiGraph

    Raises
    ------
    ValueError
    """
    if length < 0:
        raise ValueError("The lenght of the path must be >= 0")

    D = networkx.DiGraph()
    D.name = 'Directed path of length {}'.format(length)
    # vertices
    D.add_nodes_from(range(1, length+2))
    # edges
    for i in range(1, length+1):
        D.add_edge(i, i + 1)

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
            if (u, v) not in sampled_edges and \
               (v, u) not in sampled_edges and \
               not G.has_edge(u, v):
                addition.append((u, v))
                sampled_edges.add((u, v))

        if len(addition) >= m:
            return addition
        else:
            raise RuntimeError(
                "Improbable failure at sampling missing edges in a sparse graph."
            )
