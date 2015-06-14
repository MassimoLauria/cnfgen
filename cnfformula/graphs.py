#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

__docstring__ =\
"""Utilities to manage graph formats and graph files in order to build
formulas that are graph based.

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["supported_formats",
           "readGraph","writeGraph",
           "is_dag","has_bipartition",
           "bipartite_random_left_regular", "bipartite_random_regular"]

#################################################################
#          Graph Decoders (first is default)
#################################################################

_graphformats = {
    'dag':   ['kth','gml','dot'],
    'digraph': ['kth','gml','dot','dimacs'],
    'simple': ['kth','gml','dot','dimacs'],
    'bipartite': ['matrix','gml','dot']
    }

def supported_formats():
    return _graphformats



#################################################################
#          Import third party code
#################################################################

import sys

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",
          file=sys.stderr)
    exit(-1)

# remove dot format if graphviz is not installed
# we put it by default for documentation purpose
# notice that it is networkx itself that requires graphviz.
try:
    import pygraphviz
except ImportError:
    print("WARNING: Missing 'pygraphviz' library: no support for 'dot' graph format.",
          file=sys.stderr)
    for k in _graphformats.values():
        try:
            k.remove('dot')
        except ValueError:
            pass


#################################################################
#          Graph reader/writer
#################################################################

def readGraph(input_file,graph_type,file_format,multi_edges=False):
    """Read a Graph from file

    The graph are managed using the NetworkX library, and most of the
    input and output formats are the ones supported by it. Plus we
    added support for some more *hackish* formats that are useful
    in applications.

    for the "simple" and "bipartite" types, the graph is actually
    a (Multi)Graph object, while it is a (Multi)DiGraph in case of
    "dag" or "digraph".

    In the case of "dag" type, the graph is guaranteed to be acyclic
    and to pass the ``is_dag`` test. In the case of "bipartite" type,
    the graph is guaranteed to have the two parts labeled and to pass
    the ``has_bipartition`` test.


    Parameters
    -----------
    file: file object
        the input file from which the graph is read.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also ``cnfformula.graph.supported_formats()``

    file_format: string
        The file format that the parser should expect to receive.
        See also ``cnfformula.graph.supported_formats()``
    
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
        raised when either ``input_file`` is not a file object, or 
        ``graph_type`` and ``file_format`` are not valid choices

    See Also
    --------
    readGraph, is_dag, has_bipartition

    """

    if not isinstance(input_file,file):
        raise ValueError("The input object \"{}\" is not a file".format(input_file))
    
    if graph_type not in _graphformats.keys():
        raise ValueError("Wrong type. We can only read graphs of types "+_graphformats.keys())

    if graph_type in {"dag","digraph"}:
        if multi_edges:
            grtype=networkx.MultiDiGraph
        else:
            grtype=networkx.DiGraph
    else:
        if multi_edges:
            grtype=networkx.MultiGraph
        else:
            grtype=networkx.Graph

    if file_format not in _graphformats[graph_type]:
        raise ValueError("For \"{}\" type we only support these formats: ".format(graph_type)
                         +_graphformats[graph_type])

    if file_format=='dot':

        G=grtype(networkx.read_dot(input_file))

    elif file_format=='gml':

        G=grtype(networkx.read_gml(input_file))

    elif file_format=='kth':

        G=_read_graph_kth_format(input_file,grtype)

    elif file_format=='dimacs':

        G=_read_graph_dimacs_format(input_file,grtype)

    elif file_format=='matrix':

        assert graph_type=="bipartite"
        assert grtype==networkx.Graph
        G=_read_graph_matrix_format(input_file)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(file_format))

    if graph_type=="dag" and not is_dag(G):
        raise ValueError("Input graph must be acyclic")

    if graph_type=="bipartite" and not has_bipartition(G):
        raise ValueError("Input graph must be labeled with a bipartition")
        
    return G


def writeGraph(G,output_file,graph_type,file_format=None):
    """Write a graph to a file

    Parameters
    -----------
    G : networkx.Graph (or similar)

    output_file: file object
        the output file to which the graph is written.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also ``cnfformula.graph.supported_formats()``

    file_format: string, optional
        The file format that the parser should expect to receive.
        See also ``cnfformula.graph.supported_formats()``. By default
        is the first of the supported format for the value of
        ``graph_type``.
    
    Returns
    -------
    None

    Raises
    ------
    ValueError
        raised when either ``output_file`` is not a file object, or 
        ``graph_type`` and ``file_format`` are not valid choices.

    See Also
    --------
    readGraph
    """

    if not isinstance(output_file,file):
        raise ValueError("The output object \"{}\" is not a file".format(output_file))


    if graph_type not in _graphformats.keys():
        raise ValueError("Wrong type {}. We can only save graphs of types {}".format(graph_type,
                                                                                     _graphformats.keys()))

    if file_format is None:
        file_format = _graphformats[graph_type][0]

    if file_format not in _graphformats[graph_type]:
        raise ValueError("For \"{}\" type we only support these formats: ".format(graph_type)
                         +_graphformats[graph_type])

    if file_format=='dot':

        networkx.write_dot(G,output_file)

    elif file_format=='gml':

        networkx.write_gml(G,output_file)

    elif file_format=='kth':

        _write_graph_kth_format(G,output_file)

    elif file_format=='dimacs':

        _write_graph_dimacs_format(G,output_file)

    elif file_format=='matrix':

        _write_graph_matrix_format(G,output_file)
            
    else:
        raise RuntimeError("Internal error, format {} not implemented".format(file_format))

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

    if not isinstance(digraph,(networkx.MultiDiGraph,networkx.DiGraph)):
        return False

    elif hasattr(digraph,"topologically_sorted"):

        assert isinstance(digraph,(networkx.MultiDiGraph,networkx.DiGraph))
        assert hasattr(digraph,"ordered_vertices")
        assert digraph.order()==len(digraph.ordered_vertices)
        assert set(digraph.nodes())==set(digraph.ordered_vertices)
        assert networkx.algorithms.is_directed_acyclic_graph(digraph)
        return True

    else:
        return networkx.algorithms.is_directed_acyclic_graph(digraph)


def has_bipartition(G):
    """Check that the graph is labelled with a bipartition

    NetworkX follows the convention that bipartite graphs have their
    vertices labeled with the bipartition. In particular each vertex
    has the 'bipartite' attribute with is either 0 or 1.
    
    Parameters
    ----------
    G: networkx.Graph
        
    """
    try: 
        for n in G.nodes():
            if not G.node[n]['bipartite'] in [0,1]:
                return False
    except KeyError:
        return False
    
    return True


#
# Use, when possible, a fixed vertex order
#
def enumerate_vertices(graph):
    """Compute an ordered list of vertices of `graph`

    If the graph as the field `ordered_vertices` use it. Otherwise
    give an arbitrary vertex sequence.

    Arguments:
    - `graph`: input graph
    """
    if hasattr(graph,"ordered_vertices"):
        assert graph.order()==len(graph.ordered_vertices)
        assert set(graph.nodes())==set(graph.ordered_vertices)
        return graph.ordered_vertices
    else:
        return graph.nodes()

#
# In-house parsers
#

# kth reader
def _read_graph_kth_format(inputfile,graph_class=networkx.DiGraph):
    """Read a graph from file, in the KTH format.

    If the vertices are listed from to sources to the sinks, then the
    graph is marked as topologically sorted, and any DAG test will be
    answered without running any visit to the graph. Otherwise no
    assumption is made.
    
    Parameters
    ----------
    inputfile : file object
        file handle of the input
    
    graph_class: class object
        the graph class to read, one of networkx.DiGraph (default)
        networkx.MultiDiGraph networkx.Graph networkx.MultiGraph
    """
    if not graph_class in [networkx.DiGraph,
                          networkx.MultiDiGraph,
                          networkx.Graph,
                          networkx.MultiGraph]:
        raise ValueError("Internal error. Attempt to use an unsupported class for graph representation.")

    
    G=graph_class()
    G.name=''
    G.ordered_vertices=[]

    # is the input topologically sorted?
    topologically_sorted_input=True

    # vertex number
    nvertex=-1
    vertex_cnt=-1

    for i,l in enumerate(inputfile.readlines()):
        
        # add the comment to the header
        if l[0]=='c':
            G.name+=l[2:]
            continue

        if ':' not in l:
            # vertex number spec
            if nvertex>=0:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(i))
            nvertex = int(l.strip())
            if nvertex<0:
                raise ValueError("Input error: "+
                                 "Non negative number of vertices expected at line {}.".format(i))
            continue
        
        target,sources=l.split(':')
        target=int(target.strip())
        sources=[int(s) for s in sources.split()]

        # Load vertices in the graph
        if target not in G:
            G.add_node(target)
            G.ordered_vertices.append(target)

        for vertex in sources:
            if vertex not in G:
                topologically_sorted_input = False
                G.add_node(vertex)
                G.ordered_vertices.append(vertex)
              
        # after vertices, add the edges
        for s in sources:
            G.add_edge(s,target)

    # cache the information that the graph is topologically sorted.
    if topologically_sorted_input:
        G.topologically_sorted = True

    if nvertex!=G.order():
        raise ValueError("Input error: "+
                         "{} vertices expected. Got {} instead.".format(nvertex,G.order()))
    return G

def _read_graph_dimacs_format(inputfile,graph_class=networkx.Graph):
    """Read a graph simple from file, in the DIMACS edge format.

    Parameters
    ----------
    inputfile : file object
        file handle of the input
    
    graph_class: class object
        the graph class to read, one of networkx.DiGraph (default)
        networkx.MultiDiGraph networkx.Graph networkx.MultiGraph
    """
    if not graph_class in [networkx.Graph,
                           networkx.MultiGraph,
                           networkx.DiGraph,
                           networkx.MultiDiGraph]:
        raise ValueError("Internal error. Attempt to use an unsupported class for graph representation.")
    
    G=graph_class()
    G.name=''

    n = -1
    m = -1
    m_cnt = 0
    
    # is the input topologically sorted?
    for i,l in enumerate(inputfile.readlines()):
        
        # add the comment to the header
        if l[0]=='c':
            G.name+=l[2:]
            continue

        # parse spec line
        if l[0]=='p':
            if n>=0:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(i))
            _,fmt,nstr,mstr = l.split()
            if fmt!='edge':
                raise ValueError("Input error: "+
                                 "Dimacs \'edge\' format expected.")
            n = int(nstr)
            m = int(mstr)
            G.add_nodes_from(xrange(1,n+1))
            continue

        # parse spec line
        if l[0]=='e':
            m_cnt +=1
            _,v,w=l.split()
            G.add_edge(int(v),int(w))

    if m!=m_cnt:
        raise ValueError("Syntax error: "+
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
    G : networkx.Graph

    """
    G=networkx.Graph()
    G.name=''

    def scan_integer(inputfile):

        num_buffer = []
        line_cnt = 0

        while(True):
            if len(num_buffer)==0:

                line = inputfile.readline()

                if len(line)==0: raise StopIteration # end of file
                
                line_cnt += 1
                tokens = line.split()

                if len(tokens)==0 or tokens[0][0]=='#': continue # comment line
                
                try:
                    num_buffer.extend( (int(lit),line_cnt) for lit in tokens )
                except ValueError:
                    raise ValueError("Syntax error: "+
                                     "line {} contains a non numeric entry.".format(line_cnt))
        
            yield num_buffer.pop(0)

    
    scanner = scan_integer(inputfile)

    try:
        n = scanner.next()[0]
        m = scanner.next()[0]

        # bipartition of vertices
        for i in range(1,n+1):
            G.add_node(i,bipartite=0)
        for i in range(n+1,n+m+1):
            G.add_node(i,bipartite=1)

        # read edges
        for i in range(1,n+1):
            for j in range(n+1,n+m+1):
                
                (b,l) = scanner.next()
                if b==1:
                    G.add_edge(i,j)
                elif b==0:
                    pass
                else:
                    raise ValueError("Input error at line {}: only 0 or 1 are allowed".format(l))
    except StopIteration:
        raise ValueError("Input error: unexpected end of the matrix")

    # check that there are is no more data
    try:
        (b,l) = scanner.next()
        raise ValueError("Input error at line {}: there are more than {}x{} entries".format(l,n,m))
    except StopIteration:
        pass
    
    assert has_bipartition(G)
    return G


#
# In-house graph writers
#
def _write_graph_kth_format(G,output_file):
    """Wrire a graph to a file, in the KTH format.
    
    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    print("c {}".format(G.name),file=output_file)
    print("{}".format(G.order()),file=output_file)

    # we need numerical indices for the vertices
    enumeration = zip( enumerate_vertices(G),
                       xrange(1,G.order()+1))

    # adj list in the same order
    indices = dict( enumeration )

    from cStringIO import StringIO
    output = StringIO()

    for v,i in enumeration:

        if G.is_directed():
            neighbors = [indices[w] for w in G.predecessors(v)]

        else:
            neighbors = [indices[w] for w in G.adj[v].keys()]

        neighbors.sort()

        output.write( str(i)+" : ")
        output.write( " ".join([str(i) for i in neighbors]))
        output.write( "\n")
    
    print(output.getvalue(),file=output_file)


def  _write_graph_dimacs_format(G,output_file):
    """Wrire a graph to a file, in DIMACS format.
    
    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    print("c {}".format(G.name).strip(),file=output_file)
    vertices=dict((name,index)
                  for index,name in enumerate(G.nodes(),1))
    edges   =G.edges()
    print("p edge {} {}".format(len(vertices),len(edges)),file=output_file)

    for v,w in edges:
        print("e {} {}".format(vertices[v],vertices[w]),file=output_file)


def _write_graph_matrix_format(G,output_file):
    """Wrire a graph to a file, in \"matrix\" format.
    
    Parameters
    ----------
    G : graph object

    output_file : file object
        file handle of the output
    """

    Left  =  [v for v in G.nodes() if G.node[v]["bipartite"]==0]
    Right =  [v for v in G.nodes() if G.node[v]["bipartite"]==1]

    print("{} {}".format(len(Left),len(Right)),file=output_file)
    for u in Left:

        adj_row =[]

        for v in Right:
            if G.has_edge(u,v): adj_row.append("1")
            else: adj_row.append("0")
                
        print(" ".join(adj_row),file=output_file)

#
# Graph generator (missing from networkx)
#

def bipartite_random_left_regular(l,r,d,seed=None):
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
    if seed: random.seed(seed)
    
    if (l<0 or r<0 or d<0):
        raise ValueError("bipartite_random_left_regular(l,r,d) needs l,r,d >=0.")
 
    G=networkx.Graph()
    G.name = "bipartite_random_left_regular({},{},{})".format(l,r,d)
    
    L=range(0,l)
    R=range(l,l+r)
    if  d>r: d=r
    
    for u in L:
        G.add_node(u,bipartite=0)

    for v in R:
        G.add_node(v,bipartite=1)

    for u in L:
        for v in sorted(random.sample(R,d)):
            G.add_edge(u,v)
    
    return G


def bipartite_random_regular(l,r,d,seed=None):
    """Returns a random bipartite graph with constant degree on both sides.

    The graph is d-regular on the left side and regular on the right
    size, so it must be that d*l / r is an integer number.
    
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
    if seed: random.seed(seed)

    
    if (l<0 or r<0 or d<0):
        raise ValueError("bipartite_random_regular(l,r,d) needs l,r,d >=0.")

    if (l*d) % r != 0:
        raise ValueError("bipartite_random_regular(l,r,d) needs r to divid l*d.")
 
    G=networkx.Graph()
    G.name = "bipartite_random_regular({},{},{})".format(l,r,d)
    
    L=range(0,l)
    R=range(l,l+r)
    
    for u in L:
        G.add_node(u,bipartite=0)

    for v in R:
        G.add_node(v,bipartite=1)

    A=L*d
    B=R*(l*d / r)
    assert len(B)==l*d

    for i in range(l*d):
        # Sample an edge, do not add it if it existed
        # We expect to sample at most d^2 edges
        for retries in range(3*d*d):
            ea=random.randint(i,l*d-1)
            eb=random.randint(i,l*d-1)
            if not G.has_edge(A[ea],B[eb]):
                G.add_edge(A[ea],B[eb])
                A[i],A[ea] = A[ea],A[i]
                B[i],B[eb] = B[eb],B[i]
                break
        else:
            # Sampling takes too long, maybe no good edge exists
            failure=True
            for ea in range(i,l*d):
                for eb in range(i,l*d):
                    if not G.has_edge(A[ea],B[eb]):
                        failure=False
                        break
                if not failure:
                    break
            if failure:
                return bipartite_random_regular(l,r,d)

    return G

def _bipartite_nx_workaroud(G):
    """Workaround for bipartition labels

    The complete bipartite graph does not set the bipartite vertex
    labels appropriately.

    ..note:: 
        This will be superfluous in Networkx 2.0, since the bug was fixed there.
    """
    if G.name[:24] !='complete_bipartite_graph': return G

    right_start = min(G.adj[0])
    
    # Mark the bipartition
    for i in range(0,right_start):
        G.add_node(i,bipartite=0)
    for i in range(right_start,G.order()):
        G.add_node(i,bipartite=1)

