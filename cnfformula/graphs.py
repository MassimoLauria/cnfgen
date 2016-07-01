#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to manage graph formats and graph files in order to build
formulas that are graph based.
"""

from __future__ import print_function


__all__ = ["supported_formats",
           "readGraph","writeGraph",
           "is_dag","has_bipartition","enumerate_vertices",
           "bipartite_random_left_regular", "bipartite_random_regular",
           "dag_complete_binary_tree", "dag_pyramid"]

#################################################################
#          Graph Decoders (first is default)
#################################################################


_graphformats = { 
    'dag':   ['kthlist','gml','dot'],
    'digraph': ['kthlist','gml','dot','dimacs'],
    'simple': ['kthlist','gml','dot','dimacs'],
    'bipartite': ['matrix','gml','dot']
    }

def supported_formats():
    """The graph file formats supported by the library."""
    return _graphformats



#################################################################
#          Import third party code
#################################################################

import sys
import StringIO
import io
import os

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",
          file=sys.stderr)
    exit(-1)


def has_dot_library():
    """Test the presence of a library that supports dot format

    Old version of NetworkX have use `pydot', while new versions use
    `pydotplus`.

    read_dot and write_dot exposed in the
    main package. This is not true anymore in NetworkX 1.11.

    Furthermore the position of the `read_dot` and `write_dot` have been
    moved around between versions.

    The function returns the available reader and writer, and
    furthermore it cleans up the list of supported format from any
    reference to dot format, in case of missing library.

    """
    try:
        # newer version of networkx
        from networkx import nx_pydot
        import pydotplus
        del pydotplus
        return True
    except ImportError:
        pass

    try:
        # older version of networkx but we still require pydot > 10.28
        from networkx import read_dot,write_dot
        import pydot
        from distutils.version import StrictVersion
        pydot_current_version     = StrictVersion(pydot.__version__)
        pydot_good_enough_version = StrictVersion("1.0.29")
        if pydot_current_version < pydot_good_enough_version:
            raise ImportError
        del pydot
        return True
    except ImportError:
        pass

    return False

# Check that DOT is a supported format
if not has_dot_library():
    for k in _graphformats.values():
        try:
            k.remove('dot')
        except ValueError:
            pass


def find_read_dot():
    """Look for the implementation of 'read_dot' in NetworkX

    The position inside the NetworkX library depends on its version.
    """

    try:
        from networkx import nx_pydot
        return networkx.nx_pydot.read_dot
    except ImportError:
        pass

    try:
        from networkx import read_dot
        return read_dot
    except ImportError:
        pass

    raise RuntimeError("We can't find an implementation of 'read_dot' in NetworkX")


    
def find_write_dot():
    """Look for the implementation of 'write_dot' in NetworkX

    The position inside the NetworkX library depends on its version.
    """    
    try:
        from networkx import nx_pydot
        return networkx.nx_pydot.write_dot
    except ImportError:
        pass

    try:
        from networkx import write_dot
        return write_dot
    except ImportError:
        pass
    
    raise RuntimeError("We can't find an implementation of 'write_dot' in NetworkX")


#################################################################
#          Graph reader/writer
#################################################################


def _process_graph_io_arguments(iofile,
                                graph_type,
                                file_format,
                                multi_edges):
    """Test if the argument for the graph I/O functions make sense"""

    # Check the file
    if not isinstance(iofile,io.TextIOBase) and \
       not isinstance(iofile,file) and \
       not isinstance(iofile,StringIO.StringIO):
        raise ValueError("The IO stream \"{}\" does not correspond to a file".format(iofile))
    
    # Check the graph type specification
    if graph_type not in _graphformats.keys():
        raise ValueError("The graph type must be one of "+_graphformats.keys())

    elif graph_type in {"dag","digraph"}:
        if multi_edges:
            grtype=networkx.MultiDiGraph
        else:
            grtype=networkx.DiGraph
    elif graph_type in {"simple",'bipartite'}:
        if multi_edges:
            grtype=networkx.MultiGraph
        else:
            grtype=networkx.Graph
    else:
        raise RuntimeError("Unchecked graph type argument: {}".format(grtype))

    # Check/discover file format specification
    if file_format=='autodetect':
        try:
            extension = os.path.splitext(iofile.name)[-1][1:]
        except AttributeError:
            raise ValueError("No file name corresponds to IO stream. Can't guess a file format.")
            
        if extension not in _graphformats[graph_type]:
            raise ValueError("Cannot guess a file format for {} graphs from \"{}\".".\
                             format(graph_type,iofile.name))
        else:
            file_format=extension

    elif file_format not in _graphformats[graph_type]:
        raise ValueError("For {} graphs we only support these formats: ".format(graph_type)
                         +_graphformats[graph_type])

    return (grtype,file_format)
    


def readGraph(input_file,graph_type,file_format='autodetect',multi_edges=False):
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
    input_file: str, unicode or file-like object
        the input file from which the graph is read. If it is a string
        then the graph is read from a file with that string as
        filename. Otherwise if the input_file is a file object (or
        a text stream), the graph is read from there.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also :py:func:`cnfformula.graph.supported_formats`

    file_format: string, optional
        The file format that the parser should expect to receive.
        See also :py:func:`cnfformula.graph.supported_formats`. By default
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
    writeGraph, is_dag, has_bipartition

    """

    # file name instead of file object
    if isinstance(input_file,(str,unicode)):
        with open(input_file,'r') as file_handle:
            return readGraph(file_handle,graph_type,file_format,multi_edges)

    
    grtype, file_format = _process_graph_io_arguments(input_file,
                                                      graph_type,
                                                      file_format,
                                                      multi_edges)

    if file_format=='dot':

        G=grtype(find_read_dot()(input_file))

    elif file_format=='gml':

        try:
            G=grtype(networkx.read_gml(input_file))
        except networkx.NetworkXError,errmsg:
            raise ValueError("[Parse error in GML input] {} ".format(errmsg))

    elif file_format=='kthlist':

        G=_read_graph_kthlist_format(input_file,grtype)

    elif file_format=='dimacs':

        G=_read_graph_dimacs_format(input_file,grtype)

    elif file_format=='matrix':

        G=_read_graph_matrix_format(input_file)

    else:
        raise RuntimeError("[Internal error] Format {} not implemented".format(file_format))

    if graph_type=="dag" and not is_dag(G):
        raise ValueError("[Input error] Graph must be acyclic")

    if graph_type=="bipartite" and not has_bipartition(G):
        raise ValueError("[Input error] Graph vertices miss the 'bipartite' 0,1 label.")
        
    return G


def writeGraph(G,output_file,graph_type,file_format='autodetect'):
    """Write a graph to a file

    Parameters
    -----------
    G : networkx.Graph (or similar)

    output_file: file object
        the output file to which the graph is written. If it is a string
        then the graph is written to a file with that string as
        filename. Otherwise if ``output_file`` is a file object (or
        a text stream), the graph is written there.

    graph_type: string in {"simple","digraph","dag","bipartite"}
        see also :py:func:`cnfformula.graph.supported_formats`

    file_format: string, optional
        The file format that the parser should expect to receive.
        See also :py:func:`cnfformula.graph.supported_formats`. By default
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
    if isinstance(output_file,(str,unicode)):
        with open(output_file,'w') as file_handle:
            return writeGraph(G,file_handle,graph_type,file_format)

    
    _,file_format = _process_graph_io_arguments(output_file,
                                                graph_type,
                                                file_format,
                                                False)
    
    if file_format=='dot':

        find_write_dot()(G,output_file)

    elif file_format=='gml':

        networkx.write_gml(G,output_file)
            
    elif file_format=='kthlist':

        _write_graph_kthlist_format(G,output_file)

    elif file_format=='dimacs':

        _write_graph_dimacs_format(G,output_file)

    elif file_format=='matrix':

        _write_graph_matrix_format(G,output_file)
            
    else:
        raise RuntimeError("[Internal error] Format {} not implemented".format(file_format))

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

def bipartite_sets(G):
    Left  =  [v for v,d in G.nodes(data=True) if d['bipartite']==0]
    Right =  [v for v,d in G.nodes(data=True) if d['bipartite']==1]
    return Left, Right


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

# kth graph format reader
def _read_graph_kthlist_format(inputfile,graph_class=networkx.DiGraph):
    """Read a graph from file, in the KTH reverse adjacency lists format.

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
        raise ValueError("[Internal error] Attempt to use an unsupported class for graph representation.")

    
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

        # empty line
        if len(l.strip())==0:
            continue
        
        if ':' not in l:
            # vertex number spec
            if nvertex>=0:
                raise ValueError("[Syntax error] "+
                                 "Line {} contains a second spec directive.".format(i))
            nvertex = int(l.strip())
            if nvertex<0:
                raise ValueError("[Input error] "+
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
        raise ValueError("[Input error] "+
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
        raise ValueError("[Internal error] Attempt to use an unsupported class for graph representation.")
    
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
                raise ValueError("[Syntax error] "+
                                 "Line {} contains a second spec line.".format(i))
            _,fmt,nstr,mstr = l.split()
            if fmt!='edge':
                raise ValueError("[Input error] "+
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
        raise ValueError("[Syntax error] "+
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

        while True:
            if len(num_buffer)==0:

                line = inputfile.readline()

                if len(line)==0:
                    raise StopIteration # end of file
                
                line_cnt += 1
                tokens = line.split()

                if len(tokens)==0 or tokens[0][0]=='#':
                    continue # comment line
                
                try:
                    num_buffer.extend( (int(lit),line_cnt) for lit in tokens )
                except ValueError:
                    raise ValueError("[Syntax error] "+
                                     "Line {} contains a non numeric entry.".format(line_cnt))
        
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
                    raise ValueError("[Input error at line {}] Only 0 or 1 are allowed".format(l))
    except StopIteration:
        raise ValueError("[Input error] Unexpected end of the matrix")

    # check that there are is no more data
    try:
        (b,l) = scanner.next()
        raise ValueError("[Input error at line {}] There are more than {}x{} entries".format(l,n,m))
    except StopIteration:
        pass
    
    assert has_bipartition(G)
    return G


#
# In-house graph writers
#
def _write_graph_kthlist_format(G,output_file):
    """Wrire a graph to a file, in the KTH reverse adjacency lists format.
    
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

    Left,Right = bipartite_sets(G)

    print("{} {}".format(len(Left),len(Right)),file=output_file)
    for u in Left:

        adj_row =[]

        for v in Right:
            if G.has_edge(u,v):
                adj_row.append("1")
            else:
                adj_row.append("0")
                
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
    if seed:
        random.seed(seed)
    
    if l<0 or r<0 or d<0:
        raise ValueError("bipartite_random_left_regular(l,r,d) needs l,r,d >=0.")
 
    G=networkx.Graph()
    G.name = "bipartite_random_left_regular({},{},{})".format(l,r,d)
    
    L=range(0,l)
    R=range(l,l+r)
    d=min(r,d)
    
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
    if seed:
        random.seed(seed)

    if l<0 or r<0 or d<0:
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
    if G.name[:24] !='complete_bipartite_graph':
        return G

    right_start = min(G.adj[0])
    
    # Mark the bipartition
    for i in range(0,right_start):
        G.add_node(i,bipartite=0)
    for i in range(right_start,G.order()):
        G.add_node(i,bipartite=1)



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
    D=networkx.DiGraph()
    D.name='Pyramid of height {}'.format(height)
    D.ordered_vertices=[]

    # vertices
    X=[ [('x_{{{},{}}}'.format(h,i),h,i) for i in range(height-h+1)] \
        for h in range(height+1) ]
    
    for layer in X:
        for (name,h,i) in layer:
            D.add_node(name,rank=(h,i))
            D.ordered_vertices.append(name)

    # edges
    for h in range(1,len(X)):
        for i in range(len(X[h])):
            D.add_edge(X[h-1][i][0]  ,X[h][i][0])
            D.add_edge(X[h-1][i+1][0],X[h][i][0])

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
    D=networkx.DiGraph()
    D.name='Complete binary tree of height {}'.format(height)
    D.ordered_vertices=[]
    # vertices
    vert=['v_{}'.format(i) for i in range(1,2*(2**height))]
    for w in vert:
        D.add_node(w)
        D.ordered_vertices.append(w)
    # edges
    N=len(vert)-1
    for i in range(len(vert)//2):
        D.add_edge(vert[N-2*i-1],vert[N-i])
        D.add_edge(vert[N-2*i-2],vert[N-i])

    return D

def sample_missing_edges(G,m, seed=None):
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
    if seed:
        random.seed(seed)

    from networkx import non_edges

    if m < 0:
        raise ValueError("You can only sample a non negative number of edges.")

    
    total_number_of_edges=None
    
    if has_bipartition(G):
        
        Left,Right = bipartite_sets(G)
        total_number_of_edges = len(Left)*len(Right) 

        def edge_sampler():
            u = random.sample(Left,1)[0]
            v = random.sample(Right,1)[0]
            return (u,v)

        def available_edges():
            return [(u,v) for u in Left for v in Right if not G.has_edge(u,v)]

    else:

        total_number_of_edges = G.order()*(G.order()-1)/2 

        def edge_sampler():
            return random.sample(G.nodes(),2)

        def available_edges():
            return list(non_edges(G))


    number_avaiable_edges = total_number_of_edges - G.number_of_edges()
 
    if number_avaiable_edges < m:
        raise ValueError("The graph does not have {} missing edges to sample.".format(m))

    if G.number_of_edges() + m >=  total_number_of_edges / 2:
        # Large density case: enumerate missing edges and sample.
        return random.sample(available_edges(),m)

    else:
        # Sparse case: sample and retry
        missing_edges=set()

        for _ in xrange(100*m):

            if len(missing_edges) >= m:
                break

            u,v = edge_sampler()
            if (u,v) not in missing_edges and \
               (v,u) not in missing_edges and \
               not G.has_edge(u,v):
                missing_edges.add( (u,v) )
                
        if len(missing_edges) >= m:
            return missing_edges
        else:
            raise RuntimeError("Improbable failure at sampling missing edges in a sparse graph.")
    
